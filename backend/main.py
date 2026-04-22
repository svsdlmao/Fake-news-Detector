"""FastAPI backend for fake news detection."""
import os
import sys
import re
import numpy as np
import joblib
import torch
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification

# Add project root to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from backend.scraper import fetch_article
from backend.factcheck import find_fact_checks

app = FastAPI(title="Fake News Detector API", version="1.0.0")

# CORS — dev defaults plus any origins injected via ALLOWED_ORIGINS env var.
# Set ALLOWED_ORIGINS="https://your-app.pages.dev,https://www.yourdomain.com"
# in the Hugging Face Space secrets.
_default_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
_extra_origins = [
    o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "").split(",") if o.strip()
]
_allowed_origins = _default_origins + _extra_origins

# Also accept any *.pages.dev preview deploy so Cloudflare PR previews work.
_allowed_origin_regex = r"https://.*\.pages\.dev"

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_origin_regex=_allowed_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model references
bert_model = None
bert_tokenizer = None
baseline_model = None
baseline_vectorizer = None
model_type = None
device = None

ID2LABEL = {0: 'real', 1: 'fake'}


class TextRequest(BaseModel):
    text: str

class URLRequest(BaseModel):
    url: str

class PredictionResponse(BaseModel):
    label: str
    confidence: float
    top_words: list
    fact_checks: list = []


def preprocess_text(text):
    """Simple text preprocessing for baseline model."""
    text = str(text).lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text


def predict_bert_fast(text):
    """Fast BERT prediction using attention weights for explainability (single inference)."""
    inputs = bert_tokenizer(text, return_tensors='pt', truncation=True,
                            padding=True, max_length=256)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = bert_model(**inputs, output_attentions=True)

    probs = torch.softmax(outputs.logits, dim=-1).cpu().numpy()[0]
    pred_idx = int(np.argmax(probs))
    label = ID2LABEL[pred_idx].upper()
    confidence = float(probs[pred_idx])

    # Get word importance from attention weights (last layer, averaged across heads)
    attentions = outputs.attentions
    if attentions and len(attentions) > 0:
        # Shape: (num_heads, seq_len, seq_len)
        attention = attentions[-1][0]  # last layer, first batch item
        # CLS token's attention to all tokens, averaged across heads
        cls_attention = attention.mean(dim=0)[0].cpu().numpy()
    else:
        # Fallback: uniform attention
        seq_len = inputs['input_ids'].shape[1]
        cls_attention = np.ones(seq_len) / seq_len

    tokens = bert_tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])

    # Merge subwords and aggregate attention
    word_scores = {}
    current_word = ''
    current_score = 0.0

    for token, score in zip(tokens, cls_attention):
        if token in ['[CLS]', '[SEP]', '[PAD]']:
            continue
        if token.startswith('##'):
            current_word += token[2:]
            current_score += float(score)
        else:
            if current_word:
                word_scores[current_word] = word_scores.get(current_word, 0) + current_score
            current_word = token
            current_score = float(score)

    if current_word:
        word_scores[current_word] = word_scores.get(current_word, 0) + current_score

    # Sort by importance and take top 10
    sorted_words = sorted(word_scores.items(), key=lambda x: abs(x[1]), reverse=True)[:10]

    # Normalize weights relative to the max
    max_weight = max(abs(w) for _, w in sorted_words) if sorted_words else 1.0
    top_words = []
    for word, weight in sorted_words:
        # Positive weight = pushes toward predicted class
        # If predicted FAKE, positive = fake signal; if REAL, flip sign
        normalized = weight / max_weight
        if label == 'REAL':
            normalized = -normalized
        top_words.append({'word': word, 'weight': round(normalized, 4)})

    return {
        'label': label,
        'confidence': round(confidence, 4),
        'top_words': top_words,
    }


def predict_baseline(text):
    """Predict using baseline TF-IDF + Logistic Regression model."""
    processed = preprocess_text(text)
    X = baseline_vectorizer.transform([processed])
    proba = baseline_model.predict_proba(X)[0]
    classes = list(baseline_model.classes_)

    pred_idx = np.argmax(proba)
    label = classes[pred_idx].upper()
    confidence = float(proba[pred_idx])

    feature_names = baseline_vectorizer.get_feature_names_out()
    tfidf_scores = X.toarray()[0]
    coef = baseline_model.coef_[0]

    word_weights = tfidf_scores * coef
    nonzero = np.nonzero(tfidf_scores)[0]
    word_importance = [(feature_names[i], float(word_weights[i])) for i in nonzero]
    word_importance.sort(key=lambda x: abs(x[1]), reverse=True)

    top_words = [
        {'word': word, 'weight': round(weight, 4)}
        for word, weight in word_importance[:10]
    ]

    return {
        'label': label,
        'confidence': round(confidence, 4),
        'top_words': top_words,
    }


@app.on_event("startup")
async def load_model():
    """Load best available model at startup."""
    global bert_model, bert_tokenizer, baseline_model, baseline_vectorizer, model_type, device

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Try BERT first
    bert_dir = os.path.join(BASE_DIR, 'ml', 'models', 'bert_finetuned')
    if os.path.exists(bert_dir) and any(f.endswith('.bin') or f.endswith('.safetensors') for f in os.listdir(bert_dir)):
        try:
            bert_tokenizer = DistilBertTokenizerFast.from_pretrained(bert_dir)
            bert_model = DistilBertForSequenceClassification.from_pretrained(
                bert_dir, attn_implementation='eager')
            bert_model.to(device)
            bert_model.eval()
            model_type = "bert"
            print("BERT model loaded successfully")
            return
        except Exception as e:
            print(f"Failed to load BERT model: {e}")

    # Fall back to baseline
    baseline_path = os.path.join(BASE_DIR, 'ml', 'models', 'baseline.pkl')
    if os.path.exists(baseline_path):
        try:
            data = joblib.load(baseline_path)
            baseline_model = data['model']
            baseline_vectorizer = data['vectorizer']
            model_type = "baseline"
            print("Baseline model loaded successfully (TF-IDF + Logistic Regression)")
            return
        except Exception as e:
            print(f"Failed to load baseline model: {e}")

    print("Warning: No model found. Train a model first.")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "model": model_type or "not-loaded"}


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: TextRequest):
    """Predict if text is fake or real news."""
    if model_type is None:
        raise HTTPException(status_code=503, detail="No model loaded. Train a model first.")

    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    if model_type == "bert":
        result = predict_bert_fast(request.text)
    else:
        result = predict_baseline(request.text)

    # Fact-check lookup (non-blocking: failures won't break prediction)
    try:
        fact_checks = find_fact_checks(request.text)
    except Exception:
        fact_checks = []

    return PredictionResponse(
        label=result['label'],
        confidence=result['confidence'],
        top_words=result['top_words'],
        fact_checks=fact_checks,
    )


@app.post("/predict-url", response_model=PredictionResponse)
async def predict_url(request: URLRequest):
    """Scrape article from URL and predict if fake or real."""
    if model_type is None:
        raise HTTPException(status_code=503, detail="No model loaded. Train a model first.")

    try:
        article_text = fetch_article(request.url)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    if model_type == "bert":
        result = predict_bert_fast(article_text)
    else:
        result = predict_baseline(article_text)

    # Fact-check lookup (non-blocking: failures won't break prediction)
    try:
        fact_checks = find_fact_checks(article_text)
    except Exception:
        fact_checks = []

    return PredictionResponse(
        label=result['label'],
        confidence=result['confidence'],
        top_words=result['top_words'],
        fact_checks=fact_checks,
    )
