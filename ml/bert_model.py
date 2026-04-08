"""Fine-tune DistilBERT for fake news classification."""
import pandas as pd
import numpy as np
import os
import torch
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    Trainer,
    TrainingArguments,
)
from torch.utils.data import Dataset
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'cleaned_dataset.csv')
MODEL_DIR = os.path.join(BASE_DIR, 'ml', 'models', 'bert_finetuned')
OUTPUT_DIR = os.path.join(BASE_DIR, 'ml', 'outputs')

LABEL2ID = {'real': 0, 'fake': 1}
ID2LABEL = {0: 'real', 1: 'fake'}

class NewsDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {k: v[idx] for k, v in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx], dtype=torch.long)
        return item

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    acc = accuracy_score(labels, preds)
    return {'accuracy': acc}

def main():
    print("Loading data...")
    df = pd.read_csv(DATA_PATH)
    df['label_id'] = df['label'].map(LABEL2ID)

    train_df = df[df['split'] == 'train']
    test_df = df[df['split'] == 'test']
    val_df = df[df['split'] == 'valid'] if 'valid' in df['split'].values else test_df

    print("Tokenizing...")
    tokenizer = DistilBertTokenizerFast.from_pretrained('distilbert-base-uncased')

    train_enc = tokenizer(train_df['text'].tolist(), truncation=True, padding=True, max_length=256)
    val_enc = tokenizer(val_df['text'].tolist(), truncation=True, padding=True, max_length=256)
    test_enc = tokenizer(test_df['text'].tolist(), truncation=True, padding=True, max_length=256)

    train_dataset = NewsDataset(train_enc, train_df['label_id'].tolist())
    val_dataset = NewsDataset(val_enc, val_df['label_id'].tolist())
    test_dataset = NewsDataset(test_enc, test_df['label_id'].tolist())

    print("Loading model...")
    model = DistilBertForSequenceClassification.from_pretrained(
        'distilbert-base-uncased',
        num_labels=2,
        id2label=ID2LABEL,
        label2id=LABEL2ID,
    )

    training_args = TrainingArguments(
        output_dir=os.path.join(BASE_DIR, 'ml', 'training_output'),
        num_train_epochs=1,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=32,
        learning_rate=2e-5,
        weight_decay=0.01,
        eval_strategy='epoch',
        save_strategy='epoch',
        load_best_model_at_end=True,
        metric_for_best_model='accuracy',
        logging_steps=50,
        report_to='none',
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
    )

    print("Training...")
    trainer.train()

    print("\nEvaluating on test set...")
    preds_output = trainer.predict(test_dataset)
    preds = np.argmax(preds_output.predictions, axis=-1)
    y_test = test_df['label_id'].tolist()

    print(f"Test Accuracy: {accuracy_score(y_test, preds):.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, preds, target_names=['real', 'fake']))

    # Confusion matrix
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    cm = confusion_matrix(y_test, preds)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['real', 'fake'], yticklabels=['real', 'fake'])
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('BERT Confusion Matrix')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'confusion_matrix.png'), dpi=150)
    print(f"Confusion matrix saved to {OUTPUT_DIR}/confusion_matrix.png")

    # Save model
    model.save_pretrained(MODEL_DIR)
    tokenizer.save_pretrained(MODEL_DIR)
    print(f"Model saved to {MODEL_DIR}")

if __name__ == '__main__':
    main()
