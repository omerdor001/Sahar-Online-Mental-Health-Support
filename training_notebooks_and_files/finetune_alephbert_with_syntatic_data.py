import pandas as pd
import numpy as np
from tqdm import tqdm_pandas
from tqdm.notebook import tqdm
from transformers import BertModel, BertTokenizerFast, Trainer, TrainingArguments, AutoModelForSequenceClassification, AutoTokenizer, BertForSequenceClassification, BertTokenizer
import torch
from datasets import Dataset
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader
from sklearn.metrics import accuracy_score, precision_recall_fscore_support,  roc_auc_score, fbeta_score

import warnings
warnings.filterwarnings("ignore")

# hyperparameters
batch_size = 16
epochs = 3
learning_rate = 2e-5



model_name = 'onlplab/alephbert-base'
tokenizer = AutoTokenizer.from_pretrained(model_name)
bert_model = AutoModelForSequenceClassification.from_pretrained(model_name , num_labels=2)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
bert_model = bert_model.to(device)



messages_path = 'gems/full_dataset_with_syntatic_labeling_on_IMSR_GSR_only.csv'

messages_df = pd.read_csv(messages_path)

messages_df['engagement_id'] = messages_df['engagement_id'].astype(str)
messages_df = messages_df[messages_df['anonymized'].notna()]
messages_df['name'] = messages_df['name'].fillna('-')


# for better results we take only text from help seeker
messages_df = messages_df[messages_df['seeker'] == True]

# renaming label column (convention) and creating a Dataset object
messages_df = messages_df.rename(columns={'syntactic_risk_labels': 'label'})
messages_df['label'] = messages_df['label'].astype(int)

# split to train and test stratisfied by label
train_df, test_df = train_test_split(messages_df, test_size=0.2, stratify=messages_df['label'], random_state=42)

train_df['message_id'] = train_df['message_id'].astype(str)
test_df['message_id'] = test_df['message_id'].astype(str)



# creating Dataset objects
train_dataset = Dataset.from_pandas(train_df)
test_dataset = Dataset.from_pandas(test_df)

# mapping the text into inputs that fits the model
def tokenize(batch):
    return tokenizer(batch['anonymized'], padding='max_length', truncation=True, max_length=512)

train_dataset = train_dataset.map(tokenize, batched=True, batch_size=16)
test_dataset = test_dataset.map(tokenize, batched=True, batch_size=16)

# setting the format to pytorch tensors
train_dataset.set_format('torch', columns=['input_ids', 'attention_mask', 'label'])
test_dataset.set_format('torch', columns=['input_ids', 'attention_mask', 'label'])

train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)




optimizer = torch.optim.AdamW(bert_model.parameters(), lr=learning_rate)
bert_model.train()

#progress_bar = tqdm(range(epochs * len(train_loader)), desc="Training")
total_batches = len(train_loader)
for epoch in range(epochs):
    print(f"\nEpoch {epoch + 1}/{epochs}")
    for i, batch in enumerate(train_loader):
        optimizer.zero_grad()
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['label'].to(device)

        outputs = bert_model(input_ids, attention_mask=attention_mask, labels=labels)

        loss = outputs.loss
        loss.backward()
        optimizer.step()
        #progress_bar.update(1)
        if (i + 1) % 100 == 0:
            batches_done = i + 1
            batches_left = total_batches - batches_done
            print(f"  [Epoch {epoch + 1}] Batch {batches_done}/{total_batches} completed. {batches_left} remaining.")
            
            
            
            

bert_model.eval()
labels = []
preds = []
pred_probs = []

for batch in test_loader:
    input_ids = batch['input_ids'].to(device)
    attention_mask = batch['attention_mask'].to(device)
    label = batch['label'].to(device)

    with torch.no_grad():
        outputs = bert_model(input_ids, attention_mask=attention_mask)

    logits = outputs.logits
    probabilities = torch.softmax(logits, dim=-1)
    predictions = torch.argmax(logits, dim=-1)

    labels.extend(label.cpu().numpy())
    preds.extend(predictions.cpu().numpy())
    pred_probs.extend(probabilities[:, 1].cpu().numpy())



accuracy = accuracy_score(labels, preds)
precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='binary')
roc_auc = roc_auc_score(labels, pred_probs)
f2 = fbeta_score(labels, preds, beta=2)

print(f'Accuracy: {accuracy}')
print(f'Precision: {precision}')
print(f'Recall: {recall}')
print(f'F1: {f1}')
print(f'ROC-AUC: {roc_auc}')
print(f'F2: {f2}')

torch.save(bert_model.state_dict(), 'model_weights_anon_original.pth')