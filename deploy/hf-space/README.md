---
title: TruthLens API
emoji: 🔎
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
license: mit
short_description: DistilBERT fake news detector with fact-check lookup
---

# TruthLens API

FastAPI backend for the [TruthLens fake news detector](https://github.com/svsdlmao/Fake-news-Detector).

## Endpoints

- `GET  /health` — reports which model is loaded
- `POST /predict` — classify text (`{"text": "..."}`)
- `POST /predict-url` — scrape a URL then classify (`{"url": "..."}`)

Responses include a fine-tuned DistilBERT verdict, confidence, attention-based
word importance, and Google Fact Check Tools matches (when `GOOGLE_FACTCHECK_API_KEY`
is set in the Space secrets).

## Model artifacts

On first boot the Space loads `ml/models/bert_finetuned/` if present, otherwise
falls back to the `ml/models/baseline.pkl` TF-IDF + Logistic Regression model.
Add large model files via Git LFS before pushing, or download them at runtime in
a startup hook.

## Secrets to configure

Settings → Variables and secrets:

- `GOOGLE_FACTCHECK_API_KEY` — Google Fact Check Tools API key
- `ALLOWED_ORIGINS` — comma-separated list of frontend origins
  (e.g. `https://truthlens.pages.dev,https://truthlens-xyz.pages.dev`)
