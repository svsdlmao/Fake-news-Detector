"""FastAPI backend for fake news detection."""
import os
import sys
import re
import numpy as np
import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add project root to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from backend.scraper import fetch_article

app = FastAPI(title="Fake News Detector API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model references
predictor = None       # BERT predictor (if available)
baseline_model = None  # Baseline TF-IDF + LR (fallback)
baseline_vectorizer = None
model_type = None      # "bert" or "baseline"


class TextRequest(BaseModel):
    text: str

class URLRequest(BaseModel):
    url: str

class PredictionResponse(BaseModel):
    label: str
    confidence: float
    top_words: list


def preprocess_text(text):
    """Simple text preprocessing for baseline model."""
    text = str(text).lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text


def predict_baseline(text):
    """Predict using baseline TF-IDF + Logistic Regression model."""
    processed = preprocess_text(text)
    X = baseline_vectorizer.transform([processed])
    proba = baseline_model.predict_proba(X)[0]
    # Classes are sorted alphabetically: ['fake', 'real']
    classes = list(baseline_model.classes_)
    fake_idx = classes.index('fake')
    real_idx = classes.index('real')

    pred_idx = np.argmax(proba)
    label = classes[pred_idx].upper()
    confidence = float(proba[pred_idx])

    # Get top feature weights for explainability
    feature_names = baseline_vectorizer.get_feature_names_out()
    tfidf_scores = X.toarray()[0]
    coef = baseline_model.coef_[0]  # coefficients for the first class (fake)

    # Word importance = tfidf_score * coefficient
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
    global predictor, baseline_model, baseline_vectorizer, model_type

    # Try BERT first
    bert_dir = os.path.join(BASE_DIR, 'ml', 'models', 'bert_finetuned')
    if os.path.exists(bert_dir) and any(f.endswith('.bin') or f.endswith('.safetensors') for f in os.listdir(bert_dir)):
        try:
            from ml.explainability import BertPredictor
            predictor = BertPredictor(bert_dir)
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
        from ml.explainability import explain_text
        result = explain_text(request.text, predictor=predictor, num_features=10, num_samples=300)
    else:
        result = predict_baseline(request.text)

    return PredictionResponse(
        label=result['label'],
        confidence=result['confidence'],
        top_words=result['top_words'],
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
        from ml.explainability import explain_text
        result = explain_text(article_text, predictor=predictor, num_features=10, num_samples=300)
    else:
        result = predict_baseline(article_text)

    return PredictionResponse(
        label=result['label'],
        confidence=result['confidence'],
        top_words=result['top_words'],
    )
