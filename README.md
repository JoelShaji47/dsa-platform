# DSA Platform

AI-Powered Gamified DSA Learning Platform — React + FastAPI + PostgreSQL + Judge0 + Gemini.

## Stack

| Layer | Tech |
| --- | --- |
| Frontend | React 19, Vite, Tailwind CSS v4, Monaco Editor, React Router, Axios, Lucide |
| Backend | Python 3.11, FastAPI, SQLAlchemy 2, Alembic, Pydantic v2, PyJWT, passlib |
| Database | PostgreSQL 16 (Docker Compose) |
| Execution | Judge0 CE (RapidAPI now, self-host swap-ready) |
| AI Tutor | Google Gemini |

## Setup

### 1. Environment

```powershell
Copy-Item .env.example .env
```

Fill in `GEMINI_API_KEY` and `JUDGE0_API_URL` / `JUDGE0_API_KEY` / `JUDGE0_API_HOST`.

- Gemini key: https://aistudio.google.com/apikey
- Judge0 RapidAPI: subscribe at https://rapidapi.com/judge0-official/api/judge0-ce
  - `JUDGE0_API_URL=https://judge0-ce.p.rapidapi.com`
  - `JUDGE0_API_KEY=<your X-RapidAPI-Key>`
  - `JUDGE0_API_HOST=judge0-ce.p.rapidapi.com`
- To switch to self-hosted Judge0 later: set `JUDGE0_API_URL=http://localhost:2358` and clear the key/host.

### 2. Database

```powershell
docker compose up -d
```

### 3. Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

### 4. Frontend

```powershell
cd frontend
npm install
npm run dev
```

App: http://localhost:5173 (proxies `/api` to the backend)
