# Fake News Detector

## Purpose
AI-powered fake news detection system using NLP (BERT + TF-IDF baseline) with a FastAPI backend and React frontend. Includes LIME explainability and a Chrome extension.

## Tech Stack
- **ML**: Python, PyTorch, HuggingFace Transformers (DistilBERT), scikit-learn, LIME
- **Backend**: FastAPI, BeautifulSoup4, uvicorn
- **Frontend**: React 18, Tailwind CSS, Recharts, Axios
- **Chrome Extension**: Manifest V3

## Key Commands

### Backend
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm start   # runs on localhost:3000
```

### ML Training
```bash
# Step 1: Prepare data (requires LIAR dataset TSVs in data/)
python data/download_data.py

# Step 2: Train baseline model
python ml/baseline_model.py

# Step 3: Fine-tune BERT
python ml/bert_model.py

# Step 4: Run evaluation comparison
python ml/evaluate.py
```

### Tests
```bash
pytest backend/test_main.py -v
```

### Docker
```bash
docker-compose up --build    # runs both frontend and backend
make dev                     # shortcut
```

## Dataset
- **Source**: LIAR dataset (https://www.cs.ucsb.edu/~william/data/liar_dataset.zip)
- **Location**: `data/train.tsv`, `data/test.tsv`, `data/valid.tsv`
- **Processed**: `data/cleaned_dataset.csv` (columns: text, label, split)
- **Labels**: Binary (fake/real) mapped from 6-class LIAR labels

## Model Outputs
- Baseline model: `ml/models/baseline.pkl`
- Fine-tuned BERT: `ml/models/bert_finetuned/`
- Plots/reports: `ml/outputs/`

## API Endpoints
- `POST /predict` — classify text as fake/real with LIME explanation
- `POST /predict-url` — scrape URL then classify
- `GET /health` — health check
