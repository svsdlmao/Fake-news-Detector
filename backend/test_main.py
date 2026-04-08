"""Tests for FastAPI backend."""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Mock the model loading before importing app
with patch('backend.main.BertPredictor') as mock_predictor_cls:
    mock_predictor = MagicMock()
    mock_predictor.predict_proba.return_value = __import__('numpy').array([[0.1, 0.9]])
    mock_predictor_cls.return_value = mock_predictor

    from backend.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

@patch('backend.main.explain_text')
def test_predict_fake(mock_explain):
    mock_explain.return_value = {
        'label': 'FAKE',
        'confidence': 0.94,
        'top_words': [{'word': 'hoax', 'weight': 0.32}],
    }
    response = client.post("/predict", json={"text": "This is clearly fake news about aliens"})
    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "FAKE"
    assert "confidence" in data
    assert "top_words" in data

@patch('backend.main.explain_text')
def test_predict_real(mock_explain):
    mock_explain.return_value = {
        'label': 'REAL',
        'confidence': 0.87,
        'top_words': [{'word': 'study', 'weight': -0.25}],
    }
    response = client.post("/predict", json={"text": "The government announced new economic policy today"})
    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "REAL"

@patch('backend.main.explain_text')
@patch('backend.main.fetch_article')
def test_predict_url(mock_fetch, mock_explain):
    mock_fetch.return_value = "This is a scraped article about recent political events in the country"
    mock_explain.return_value = {
        'label': 'REAL',
        'confidence': 0.91,
        'top_words': [{'word': 'policy', 'weight': -0.18}],
    }
    response = client.post("/predict-url", json={"url": "https://example.com/article"})
    assert response.status_code == 200

def test_predict_empty_text():
    response = client.post("/predict", json={"text": ""})
    # Should return 400 or 503 depending on model state
    assert response.status_code in [400, 503]
