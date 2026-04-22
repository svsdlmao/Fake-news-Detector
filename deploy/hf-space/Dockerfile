# Hugging Face Spaces (Docker SDK) — TruthLens backend
FROM python:3.11-slim

# HF Spaces runs as uid 1000 and expects the app on port 7860
RUN useradd -m -u 1000 user
WORKDIR /app

# System deps for scientific Python + scraping
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# CPU-only torch keeps the image small enough for free Spaces
COPY --chown=user requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu \
       -r /app/requirements.txt

# Copy the backend package + any bundled model artifacts
COPY --chown=user backend /app/backend
COPY --chown=user ml /app/ml

# HF Spaces caches under /home/user/.cache — point HF libs there
ENV HF_HOME=/home/user/.cache/huggingface \
    TRANSFORMERS_CACHE=/home/user/.cache/huggingface \
    PYTHONUNBUFFERED=1 \
    PORT=7860

USER user
EXPOSE 7860

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
