# Fake News Detector

An AI-powered fake news detection system that classifies news articles as **FAKE** or **REAL** using NLP and provides explainability through LIME.

## Features

- **BERT-based classification** — Fine-tuned DistilBERT for accurate fake/real news detection
- **Baseline comparison** — TF-IDF + Logistic Regression baseline for benchmarking
- **LIME explainability** — See which words influenced the prediction and why
- **Web scraping** — Paste a URL and the system extracts and analyzes the article
- **Modern web UI** — React frontend with real-time results and interactive word importance charts
- **Chrome extension** — Analyze any news page directly from your browser
- **REST API** — FastAPI backend ready for integration

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
cd frontend && npm install
```

### 2. Prepare data

Download the [LIAR dataset](https://www.cs.ucsb.edu/~william/data/liar_dataset.zip) and extract `train.tsv`, `test.tsv`, `valid.tsv` into the `data/` folder.

```bash
python data/download_data.py
```

### 3. Train models

```bash
# Baseline model
python ml/baseline_model.py

# Fine-tune BERT (requires GPU recommended)
python ml/bert_model.py
```

### 4. Run the app

```bash
# Terminal 1: Backend
uvicorn backend.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend && npm start
```

Open http://localhost:3000 in your browser.

### Docker (alternative)

```bash
docker-compose up --build
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/predict` | Classify article text |
| POST | `/predict-url` | Scrape URL and classify |
| GET | `/health` | Health check |

### Example

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Scientists discover miracle cure overnight"}'
```

## Project Structure

```
fake-news-detector/
├── data/               # Dataset and preprocessing
├── ml/                 # ML models and training scripts
│   ├── models/         # Saved model artifacts
│   └── outputs/        # Plots and evaluation results
├── backend/            # FastAPI server
├── frontend/           # React web app
├── chrome-extension/   # Browser extension
├── CLAUDE.md           # Project context for Claude Code
└── docker-compose.yml  # Docker setup
```

## Tech Stack

- **ML**: PyTorch, HuggingFace Transformers, scikit-learn, LIME
- **Backend**: FastAPI, BeautifulSoup4
- **Frontend**: React, Tailwind CSS, Recharts
- **Extension**: Chrome Manifest V3

## Dataset

Uses the [LIAR dataset](https://www.cs.ucsb.edu/~william/data/liar_dataset.zip) — 12,800+ labeled political statements mapped to binary fake/real labels.

## License

MIT
