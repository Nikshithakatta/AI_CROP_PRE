# AI Crop Prediction

Full-stack crop recommendation app: **FastAPI** backend with ML models and a **React** frontend.

## Setup

### Backend

```powershell
cd backend
python -m venv .venv
..\.venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env
# Edit .env with your API keys
cd ..
.\backend\.venv\Scripts\python.exe backend\main.py
```

API: http://127.0.0.1:8000 — Docs: http://127.0.0.1:8000/docs

**ML models** (`.pkl` files) are not in this repo — they exceed GitHub's file size limit. After cloning, generate them:

```powershell
.\backend\.venv\Scripts\python.exe backend\retrain_model.py
```

Place trained models in `backend/models/` (the app loads them on startup).

### Frontend

```powershell
cd frontend
npm install
npm start
```

App: http://localhost:3000

## Environment variables

See `backend/.env.example`. Required:

- `API_KEY_SECRET` — must match the `X-API-Key` header the frontend sends (default: `AI_CROP_SECRET_2024`)
- `DATA_GOV_IN_API_KEY` — soil data from data.gov.in
- `OPEN_METEO_BASE_URL` — weather API (no key needed for Open-Meteo)

## Push to GitHub

```powershell
git remote add origin https://github.com/YOUR_USERNAME/AI_CROP_PRE.git
git branch -M main
git push -u origin main
```

Do not commit `backend/.env` — it is listed in `.gitignore`.
