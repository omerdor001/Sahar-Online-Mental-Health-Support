import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from transformers import AutoTokenizer, BertModel
from lime.lime_text import LimeTextExplainer
import shap
import re
import json

file_path = "data.json"
with open(file_path, "r", encoding="utf-8") as file:
    messages = json.load(file)


model_id = 'onlplab/alephbert-base'
tokenizer = AutoTokenizer.from_pretrained(model_id)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


class KeyMessagesBertClassifier(nn.Module):
    def __init__(self, model_name, num_classes=2, k=5, device=device):
        super(KeyMessagesBertClassifier, self).__init__()
        self.bert = BertModel.from_pretrained(model_name).to(device)
        self.k = k
        self.classifier = nn.Linear(self.bert.config.hidden_size, num_classes)
        self.dropout = nn.Dropout(p=0.1)

        nn.init.xavier_normal_(self.classifier.weight)
        nn.init.zeros_(self.classifier.bias)

    def forward(self, input_ids, attention_mask, segmented_input_ids, segmented_attention_mask, is_train=True):
        bert_output = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        bert_output = bert_output.last_hidden_state
        cls_output = bert_output[:, 0, :]
        cls_output = self.dropout(cls_output)
        logits = self.classifier(cls_output)

        if is_train:
            return logits, None

        num_messages = segmented_input_ids.shape[0]
        segmented_batch_size = 64
        segmented_cls_outputs = []
        for batch_start in range(0, num_messages, segmented_batch_size):
            batch_end = min(batch_start + segmented_batch_size, num_messages)
            batch_input_ids = segmented_input_ids[batch_start:batch_end]
            batch_attention_mask = segmented_attention_mask[batch_start:batch_end]

            with torch.no_grad():
                batch_output = self.bert(input_ids=batch_input_ids, attention_mask=batch_attention_mask)
                batch_cls_output = batch_output.last_hidden_state[:, 0, :]
                segmented_cls_outputs.append(batch_cls_output)

        segmented_cls_outputs = torch.cat(segmented_cls_outputs, dim=0)

        distances = torch.cdist(cls_output, segmented_cls_outputs.view(num_messages, -1), p=2)
        distances = distances.view(-1)
        top_k_indices = torch.topk(distances, min(self.k, num_messages), sorted=True).indices

        return logits, top_k_indices

# Load the model
model_path = 'alephbert_sr'
model = KeyMessagesBertClassifier(model_id).to(device)
model.load_state_dict(torch.load(model_path, map_location=device))

def process_text(messages, tokenizer, device=device, max_length=512):
    joined_text = " ".join(messages)
    joined_encoding = tokenizer(joined_text, max_length=max_length, padding='max_length', truncation=True, return_tensors='pt').to(device)
    separate_encodings = [tokenizer(msg, max_length=max_length, padding='max_length', truncation=True, return_tensors='pt').to(device) for msg in messages]

    separate_input_ids = torch.cat([enc['input_ids'] for enc in separate_encodings], dim=0)
    separate_attention_masks = torch.cat([enc['attention_mask'] for enc in separate_encodings], dim=0)

    return (
        joined_encoding['input_ids'],
        joined_encoding['attention_mask'],
        separate_input_ids,
        separate_attention_masks
    )


# process the text for the model
output = []
for message in messages:
  input_ids, attention_mask, segmented_input_ids, segmented_attention_mask = process_text([message], tokenizer)

  # get the model output
  logits, top_k_indices = model(input_ids, attention_mask, segmented_input_ids, segmented_attention_mask, is_train=False)
  top_k_indices = top_k_indices.cpu().numpy()
  probs = torch.softmax(logits, dim=1)
  prediction = torch.argmax(logits, dim=1).item()
  output.append({"message":message, "probs":probs.tolist()[0], "pred":prediction})


with open("out.json", "w", encoding="utf-8") as json_file:
    json.dump(output, json_file, ensure_ascii=False, indent=4)

print(output)

