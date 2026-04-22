# TruthLens — Fake News Detector

An AI-powered fake news detection system that classifies news articles as **FAKE** or **REAL** using a fine-tuned DistilBERT, with attention-based word importance and Google Fact Check lookups.

## Live demo

- **App:** https://truthlens-y91.pages.dev
- **API:** https://svsdlmao-truthlens.hf.space (`/health`, `/predict`, `/predict-url`)

Frontend runs on **Cloudflare Pages**, backend runs on **Hugging Face Spaces** (Docker, free CPU). See [`DEPLOY.md`](./DEPLOY.md) for the full deploy walkthrough.

```bash
curl -X POST https://svsdlmao-truthlens.hf.space/predict \
  -H 'Content-Type: application/json' \
  -d '{"text":"Scientists reveal the moon landing was faked."}'
# → {"label":"FAKE","confidence":0.84, ...}
```

## Features

- **BERT-based classification** — Fine-tuned DistilBERT for accurate fake/real news detection (~4s per request on CPU)
- **Baseline comparison** — TF-IDF + Logistic Regression baseline for benchmarking
- **Attention-based explainability** — Top words that drove the prediction, pulled from the model's last-layer attention in a single forward pass
- **Live fact-check lookup** — Google Fact Check Tools API surfaces Snopes, PolitiFact, FactCheck.org, Reuters, AP verdicts when they exist
- **Web scraping** — Paste a URL and the system extracts and analyzes the article
- **Modern web UI** — React frontend with glass-morphism design, animated confidence ring, and interactive word importance chart
- **Chrome extension** — Analyze any news page directly from your browser
- **REST API** — FastAPI backend with CORS-hardened production deploy

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

- **ML**: PyTorch, HuggingFace Transformers (DistilBERT), scikit-learn
- **Backend**: FastAPI, BeautifulSoup4 — hosted on Hugging Face Spaces (Docker)
- **Frontend**: React 18, Tailwind CSS, Recharts — hosted on Cloudflare Pages
- **Extension**: Chrome Manifest V3

## Dataset

Uses the [LIAR dataset](https://www.cs.ucsb.edu/~william/data/liar_dataset.zip) — 12,800+ labeled political statements mapped to binary fake/real labels.

## License

MIT
