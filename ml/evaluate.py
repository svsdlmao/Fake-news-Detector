"""Evaluate and compare baseline vs BERT models on fake news test set."""
import pandas as pd
import numpy as np
import os
import joblib
import torch
from sklearn.metrics import (accuracy_score, f1_score, precision_score,
                             recall_score, roc_curve, auc, classification_report)
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'cleaned_dataset.csv')
OUTPUT_DIR = os.path.join(BASE_DIR, 'ml', 'outputs')
BASELINE_PATH = os.path.join(BASE_DIR, 'ml', 'models', 'baseline.pkl')
BERT_DIR = os.path.join(BASE_DIR, 'ml', 'models', 'bert_finetuned')

LABEL2ID = {'real': 0, 'fake': 1}

def load_test_data():
    df = pd.read_csv(DATA_PATH)
    test_df = df[df['split'] == 'test']
    return test_df['text'].tolist(), test_df['label'].map(LABEL2ID).tolist()

def evaluate_baseline(texts, labels):
    """Evaluate baseline TF-IDF + LR model."""
    data = joblib.load(BASELINE_PATH)
    model, vectorizer = data['model'], data['vectorizer']

    from ml.baseline_model import preprocess_text
    processed = [preprocess_text(t) for t in texts]
    X = vectorizer.transform(processed)

    preds = model.predict(X)
    pred_ids = [LABEL2ID[p] for p in preds]
    proba = model.predict_proba(X)[:, 1]  # probability of 'fake'

    return pred_ids, proba

def evaluate_bert(texts, labels):
    """Evaluate fine-tuned BERT model."""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    tokenizer = DistilBertTokenizerFast.from_pretrained(BERT_DIR)
    model = DistilBertForSequenceClassification.from_pretrained(BERT_DIR)
    model.to(device)
    model.eval()

    pred_ids = []
    probas = []
    batch_size = 32

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        inputs = tokenizer(batch, return_tensors='pt', truncation=True,
                          padding=True, max_length=256)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=-1).cpu().numpy()
        pred_ids.extend(np.argmax(probs, axis=-1).tolist())
        probas.extend(probs[:, 1].tolist())

    return pred_ids, np.array(probas)

def plot_metrics_comparison(metrics, save_path):
    """Plot grouped bar chart comparing metrics."""
    metric_names = ['Accuracy', 'F1', 'Precision', 'Recall']
    baseline_vals = [metrics['baseline'][m] for m in ['accuracy', 'f1', 'precision', 'recall']]
    bert_vals = [metrics['bert'][m] for m in ['accuracy', 'f1', 'precision', 'recall']]

    x = np.arange(len(metric_names))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width/2, baseline_vals, width, label='Baseline (TF-IDF + LR)', color='#3498db')
    ax.bar(x + width/2, bert_vals, width, label='BERT', color='#e74c3c')

    ax.set_ylabel('Score')
    ax.set_title('Model Comparison: Baseline vs BERT')
    ax.set_xticks(x)
    ax.set_xticklabels(metric_names)
    ax.legend()
    ax.set_ylim(0, 1)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    print(f"Metrics comparison saved to {save_path}")
    plt.close()

def plot_roc_curves(labels, baseline_proba, bert_proba, save_path):
    """Plot ROC curves for both models."""
    fig, ax = plt.subplots(figsize=(8, 8))

    for name, proba, color in [('Baseline', baseline_proba, '#3498db'), ('BERT', bert_proba, '#e74c3c')]:
        fpr, tpr, _ = roc_curve(labels, proba)
        roc_auc = auc(fpr, tpr)
        ax.plot(fpr, tpr, color=color, lw=2, label=f'{name} (AUC = {roc_auc:.3f})')

    ax.plot([0, 1], [0, 1], 'k--', lw=1)
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title('ROC Curve Comparison')
    ax.legend(loc='lower right')
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    print(f"ROC curves saved to {save_path}")
    plt.close()

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    texts, labels = load_test_data()
    print(f"Test set: {len(texts)} samples\n")

    metrics = {}

    # Baseline
    print("Evaluating baseline model...")
    try:
        bl_preds, bl_proba = evaluate_baseline(texts, labels)
        metrics['baseline'] = {
            'accuracy': accuracy_score(labels, bl_preds),
            'f1': f1_score(labels, bl_preds),
            'precision': precision_score(labels, bl_preds),
            'recall': recall_score(labels, bl_preds),
        }
        print("Baseline done.")
    except Exception as e:
        print(f"Baseline evaluation failed: {e}")
        metrics['baseline'] = {'accuracy': 0, 'f1': 0, 'precision': 0, 'recall': 0}
        bl_proba = None

    # BERT
    print("Evaluating BERT model...")
    try:
        bert_preds, bert_proba = evaluate_bert(texts, labels)
        metrics['bert'] = {
            'accuracy': accuracy_score(labels, bert_preds),
            'f1': f1_score(labels, bert_preds),
            'precision': precision_score(labels, bert_preds),
            'recall': recall_score(labels, bert_preds),
        }
        print("BERT done.")
    except Exception as e:
        print(f"BERT evaluation failed: {e}")
        metrics['bert'] = {'accuracy': 0, 'f1': 0, 'precision': 0, 'recall': 0}
        bert_proba = None

    # Print markdown table
    print("\n## Model Comparison Results\n")
    print("| Metric    | Baseline (TF-IDF+LR) | BERT (DistilBERT) |")
    print("|-----------|----------------------|-------------------|")
    for metric in ['accuracy', 'f1', 'precision', 'recall']:
        bl = metrics['baseline'][metric]
        bt = metrics['bert'][metric]
        print(f"| {metric.capitalize():9s} | {bl:.4f}               | {bt:.4f}            |")

    # Plots
    plot_metrics_comparison(metrics, os.path.join(OUTPUT_DIR, 'metrics_comparison.png'))
    if bl_proba is not None and bert_proba is not None:
        plot_roc_curves(labels, bl_proba, bert_proba, os.path.join(OUTPUT_DIR, 'roc_curves.png'))

if __name__ == '__main__':
    main()
