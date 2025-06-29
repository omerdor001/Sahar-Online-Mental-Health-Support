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
epochs = 1
learning_rate = 2e-5



model_name = 'onlplab/alephbert-base'
tokenizer = AutoTokenizer.from_pretrained(model_name)
bert_model = AutoModelForSequenceClassification.from_pretrained(model_name , num_labels=2)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
bert_model = bert_model.to(device)



conv_info_path = 'trainDatasets/conv_info.csv'
conv_info_df = pd.read_csv(conv_info_path)
conv_info_df['engagement_id'] = conv_info_df['engagement_id'].astype(str)
conv_info_df = conv_info_df.rename(columns={'gsr': 'label'})
train_conv_df, test_conv_df = train_test_split(conv_info_df, test_size=0.2, stratify=conv_info_df['label'],random_state=42)



all_messages_path = 'trainDatasets/messages_anonymized.csv'

all_messages_df = pd.read_csv(all_messages_path)

all_messages_df['engagement_id'] = all_messages_df['engagement_id'].astype(str)
all_messages_df = all_messages_df[all_messages_df['anonymized'].notna()]
all_messages_df['name'] = all_messages_df['name'].fillna('-')
all_messages_df = all_messages_df[all_messages_df["seeker"]]

#split to train and test base on conversation split and concat messages
train_all_messages_df = pd.read_csv('trainDatasets/low_resrc_augmented_trainset_4_times_bigger.csv')
train_all_messages_df = train_all_messages_df.drop(['index' , 'augmented'], axis=1)
train_all_messages_df = train_all_messages_df.sample(frac=1)

test_all_messages_df = all_messages_df[all_messages_df["engagement_id"].isin(test_conv_df["engagement_id"])]
test_all_messages_df = test_all_messages_df.merge(test_conv_df , on="engagement_id")
test_all_messages_df = test_all_messages_df.groupby('engagement_id').agg({'anonymized': '[SEP]'.join, 'label': 'first'}).reset_index()



# mapping the text into inputs that fits the model
def tokenize(batch):
    return tokenizer(batch['anonymized'], padding='max_length', truncation=True, max_length=512)

def make_weighted_train_loaders(dfs, weights, tokenize):
    #make sampled df
    acc_train = pd.DataFrame(data= {})
    for df, weight in zip(dfs,weights):
        sample = df.sample(frac = weight)
        acc_train = pd.concat([acc_train,sample[["anonymized" , "label"]]])
    
    #create datasets
    train_dataset = Dataset.from_pandas(acc_train)
    train_dataset = train_dataset.map(tokenize, batched=True, batch_size=16)
    train_dataset.set_format('torch', columns=['input_ids', 'attention_mask', 'label'])
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    return train_loader

def make_test_loader(df, tokenize):
    dataset = Dataset.from_pandas(df)
    dataset = dataset.map(tokenize, batched=True, batch_size=16)
    dataset.set_format('torch', columns=['input_ids', 'attention_mask', 'label'])
    test_loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)
    return test_loader




all_messages_test_loader = make_test_loader(test_all_messages_df, tokenize)
all_messages_train_loader = make_weighted_train_loaders([train_all_messages_df],[1],tokenize)


def calc_matrics(labels, preds, pred_probs):
    accuracy = accuracy_score(labels, preds)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='binary')
    roc_auc = roc_auc_score(labels, pred_probs)
    f2 = fbeta_score(labels, preds, beta=2)
    
    return {
    'Accuracy': accuracy,
    'Precision': precision,
    'Recall': recall,
    'F1': f1,
    'ROC-AUC': roc_auc,
    'F2': f2
    }

def eval(eval_loader):
    bert_model.eval()
    labels = []
    preds = []
    pred_probs = []
    
    for batch in eval_loader:
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
    
    return calc_matrics(labels,preds,pred_probs)


def general_trainer(train_loader, loss_fn=None):
    optimizer = torch.optim.AdamW(bert_model.parameters(), lr=learning_rate)
    bert_model.train()
    
    total_batches = len(train_loader)
    for i, batch in enumerate(train_loader):
        optimizer.zero_grad()
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['label'].to(device)
        
        outputs = bert_model(input_ids, attention_mask=attention_mask, labels=labels)
        if loss_fn is None:
            loss = outputs.loss
        else:
            loss = loss_fn(outputs, labels)
        
        loss.backward()
        optimizer.step()
        #progress_bar.update(1)
        if (i + 1) % 1000 == 0:
            batches_done = i + 1
            batches_left = total_batches - batches_done
            print(f"Batch {batches_done}/{total_batches} completed. {batches_left} remaining.")



for i in range(epochs):
    general_trainer(all_messages_train_loader)


print(eval(all_messages_test_loader))