import os

import torch
import pandas as pd
import torch.nn.functional as F
from transformers import BertTokenizer, BertForSequenceClassification
import threading
import time

class GSRAlgorithm:
    def __init__(self):
        model_name = 'onlplab/alephbert-base'

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.bert_model = BertForSequenceClassification.from_pretrained(model_name, num_labels=2).to(self.device)
        self.tokenizer = BertTokenizer.from_pretrained(model_name)

        # loading modal and setting it to eval mode to avoid parameters change while predicting
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct the relative path to the model file
        model_path = os.path.join(
            current_dir,
            "bert_model.pth",
        )
        self.bert_model.load_state_dict(torch.load(model_path, map_location=torch.device("cpu")))

    # role = ['counselor', 'help seeker', 'counselor', 'help seeker', 'counselor']
    # texts = ['text 1', 'text 2', 'text 3', 'text 4', 'text 5']
    def process(self, roles_texts: list[tuple[list[str], list[str]]]):
        batch_input_ids = []
        batch_attention_masks = []
        for roles, texts in roles_texts:
            conv_df = pd.DataFrame({'role': roles, 'text': texts})
            conversation_text = conv_df['text'].tolist()
            conversation_text = '[SEP]'.join(conversation_text)

            # tokenize and take last 512 tokens
            tokens = self.tokenizer(conversation_text, truncation=True, padding='max_length', max_length=512,
                                    return_tensors='pt')

            batch_input_ids.append(tokens['input_ids'])
            batch_attention_masks.append(tokens['attention_mask'])

        batch_input_ids = torch.cat(batch_input_ids, dim=0).to(self.device)
        batch_attention_masks = torch.cat(batch_attention_masks, dim=0).to(self.device)

        self.bert_model.eval()

        with torch.no_grad():
            outputs = self.bert_model(batch_input_ids, attention_mask=batch_attention_masks)


        probabilities = torch.softmax(outputs.logits, dim=1).detach().numpy()
        return probabilities
