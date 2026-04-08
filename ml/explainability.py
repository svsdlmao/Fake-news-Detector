"""LIME explainability for the fine-tuned BERT fake news classifier."""
import numpy as np
import os
import torch
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
from lime.lime_text import LimeTextExplainer
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, 'ml', 'models', 'bert_finetuned')
OUTPUT_DIR = os.path.join(BASE_DIR, 'ml', 'outputs')

ID2LABEL = {0: 'real', 1: 'fake'}

class BertPredictor:
    """Wrapper for BERT model to work with LIME."""
    def __init__(self, model_dir):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.tokenizer = DistilBertTokenizerFast.from_pretrained(model_dir)
        self.model = DistilBertForSequenceClassification.from_pretrained(model_dir)
        self.model.to(self.device)
        self.model.eval()

    def predict_proba(self, texts):
        """Return prediction probabilities for a list of texts."""
        results = []
        for text in texts:
            inputs = self.tokenizer(text, return_tensors='pt', truncation=True,
                                    padding=True, max_length=256)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            with torch.no_grad():
                outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1).cpu().numpy()[0]
            results.append(probs)
        return np.array(results)

def explain_text(text, predictor=None, num_features=10, num_samples=500):
    """Generate LIME explanation for a given text."""
    if predictor is None:
        predictor = BertPredictor(MODEL_DIR)

    explainer = LimeTextExplainer(class_names=['real', 'fake'])
    explanation = explainer.explain_instance(
        text, predictor.predict_proba,
        num_features=num_features, num_samples=num_samples
    )

    probs = predictor.predict_proba([text])[0]
    pred_label = ID2LABEL[np.argmax(probs)]
    confidence = float(np.max(probs))

    top_words = []
    for word, weight in explanation.as_list():
        top_words.append({'word': word, 'weight': round(weight, 4)})

    return {
        'label': pred_label.upper(),
        'confidence': round(confidence, 4),
        'top_words': top_words,
    }

def plot_explanation(top_words, save_path=None):
    """Plot a bar chart of word importance."""
    words = [w['word'] for w in top_words]
    weights = [w['weight'] for w in top_words]
    colors = ['#e74c3c' if w > 0 else '#2ecc71' for w in weights]

    plt.figure(figsize=(10, 6))
    plt.barh(words[::-1], weights[::-1], color=colors[::-1])
    plt.xlabel('Weight (positive = fake, negative = real)')
    plt.title('LIME Explanation: Top Words Influencing Prediction')
    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=150)
        print(f"Explanation plot saved to {save_path}")
    plt.close()

def main():
    sample_text = "Scientists discover new cure for cancer in groundbreaking study published today"
    print(f"Analyzing: {sample_text}\n")

    result = explain_text(sample_text)
    print(f"Prediction: {result['label']} (confidence: {result['confidence']:.2%})")
    print("\nTop words:")
    for w in result['top_words']:
        direction = "→ FAKE" if w['weight'] > 0 else "→ REAL"
        print(f"  {w['word']:20s} {w['weight']:+.4f}  {direction}")

    plot_path = os.path.join(OUTPUT_DIR, 'lime_explanation.png')
    plot_explanation(result['top_words'], save_path=plot_path)

if __name__ == '__main__':
    main()
