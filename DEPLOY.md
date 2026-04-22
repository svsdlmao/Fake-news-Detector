# Deploying TruthLens

Two pieces, two hosts:

| Layer    | Host                     | Why                                                  |
| -------- | ------------------------ | ---------------------------------------------------- |
| Frontend | **Cloudflare Pages**     | Git-connected static host, global edge, free tier.   |
| Backend  | **Hugging Face Spaces**  | Runs Docker + PyTorch + DistilBERT on a free CPU.    |

Cloudflare Workers/Pages Functions can't run PyTorch (package-size + cold-start
limits), so the ML backend lives on HF Spaces and the React SPA talks to it
over HTTPS.

---

## 1. Deploy the backend to Hugging Face Spaces

### 1a. Create the Space

1. Go to <https://huggingface.co/new-space>.
2. Owner: your account. Name: `truthlens` (or similar).
3. **SDK: Docker** → **Blank** template. Hardware: CPU basic (free).
4. Visibility: Public. Click *Create Space*.

### 1b. Push the code

HF gives you a git URL like `https://huggingface.co/spaces/<user>/truthlens`.

```bash
# From a scratch directory — NOT inside this repo
git clone https://huggingface.co/spaces/<user>/truthlens hf-space
cd hf-space

# Copy the staged Space files + the backend/ML code from this repo
cp -r /path/to/Fake-news-Detector/deploy/hf-space/. .
cp -r /path/to/Fake-news-Detector/backend .
cp -r /path/to/Fake-news-Detector/ml .

# Install git-lfs once, then track the model weights
git lfs install
git add .gitattributes
git add Dockerfile requirements.txt README.md backend ml
git commit -m "Initial TruthLens backend"
git push
```

The Space will build the Docker image (5–10 min the first time). Watch the
*Logs* tab for build progress. When it's done, the Space URL looks like:

```
https://<user>-truthlens.hf.space
```

Hit `https://<user>-truthlens.hf.space/health` — it should return
`{"status":"ok","model":"bert"}`.

### 1c. Add secrets

In the Space: **Settings → Variables and secrets → New secret**.

| Name                        | Value                                                     |
| --------------------------- | --------------------------------------------------------- |
| `GOOGLE_FACTCHECK_API_KEY`  | your Google Fact Check Tools API key                      |
| `ALLOWED_ORIGINS`           | `https://truthlens.pages.dev` (add your custom domain too)|

Click *Factory rebuild* so the new env vars are picked up.

---

## 2. Deploy the frontend to Cloudflare Pages

### 2a. Connect the repo

1. <https://dash.cloudflare.com/> → **Workers & Pages** → **Create** → **Pages**
   → **Connect to Git**.
2. Pick `svsdlmao/Fake-news-Detector`.
3. Framework preset: **Create React App**.
4. Build settings:

   | Field                 | Value                |
   | --------------------- | -------------------- |
   | Root directory        | `frontend`           |
   | Build command         | `npm run build`      |
   | Build output dir      | `build`              |
   | Node version          | `20` (via `.nvmrc`)  |

5. **Environment variables** (Production and Preview):

   | Name                | Value                                   |
   | ------------------- | --------------------------------------- |
   | `REACT_APP_API_URL` | `https://<user>-truthlens.hf.space`     |
   | `CI`                | `false` (CRA treats warnings as errors otherwise) |

6. *Save and Deploy*. First build takes ~2 min.

You'll get a URL like `https://truthlens.pages.dev`.

### 2b. Lock the CORS origin on the backend

Once the Pages URL is final, update the Space's `ALLOWED_ORIGINS` secret to
include it exactly, then *Factory rebuild* the Space.

---

## 3. Smoke test

```bash
curl -s https://<user>-truthlens.hf.space/health
# → {"status":"ok","model":"bert"}

curl -s -X POST https://<user>-truthlens.hf.space/predict \
  -H 'Content-Type: application/json' \
  -d '{"text":"Breaking: scientists say the moon is made of cheese."}'
```

Then open `https://truthlens.pages.dev` and paste an article.

---

## Troubleshooting

- **HF Space build fails on torch install** → the `extra-index-url` line in the
  `Dockerfile` pulls the CPU-only wheel. Don't change it.
- **Space boots but `/health` says `model: not-loaded`** → the model files
  weren't committed via Git LFS. From the `hf-space` clone:
  `git lfs ls-files` should list the `.safetensors` weights.
- **CORS error in the browser console** → confirm the Pages URL is in the
  Space's `ALLOWED_ORIGINS` secret *and* that you clicked *Factory rebuild*.
- **Pages build says "Treating warnings as errors"** → add `CI=false` env var.
- **Cold start is slow** → first request after idle can take 30–60s while the
  Space wakes. Upgrade the Space to "always on" ($0.60/day) if that's a problem.
