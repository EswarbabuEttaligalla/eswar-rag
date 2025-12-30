# Deployment Guide

## Environment Model

This project uses one codebase with three runtime modes:

- Local development: frontend on `http://localhost:3000`, backend on `http://localhost:8011`.
- Docker Compose: frontend on `http://localhost:3000`, backend API on `http://localhost:8000`.
- Production deploys: frontend can be static on Vercel, backend can live on Render or another HTTPS host.

The frontend now supports both patterns:

- Relative API path for local dev and Docker: `VITE_API_BASE_PATH=/api/v1`
- Absolute backend origin for Vercel/static hosting: `VITE_API_URL=https://your-backend.onrender.com`

## Recommended `.env.example`

Use this as the baseline template in the repository root.

```dotenv
APP_NAME=Private Knowledge Assistant
ENV=development
DEBUG=false
SECRET_KEY=CHANGE_ME_TO_A_LONG_RANDOM_VALUE

# Local development and Docker proxy defaults.
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:5174

# Local development defaults.
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=rag
POSTGRES_USER=rag
POSTGRES_PASSWORD=rag
DATABASE_URL=sqlite+aiosqlite:///backend/data/app.db

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

DATA_DIR=/data
UPLOAD_DIR=/data/uploads
VECTOR_DIR=/data/vectors

VECTOR_STORE=chroma
CHROMA_HOST=localhost
CHROMA_PORT=8001
CHROMA_COLLECTION=documents
PINECONE_API_KEY=
PINECONE_ENV=us-east-1
PINECONE_INDEX=rag-documents

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_CACHE_TTL_SECONDS=86400
MAX_BATCH_EMBEDDINGS=64

CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_CONTEXT_CHUNKS=6
HYBRID_ALPHA=0.7

LLM_PROVIDER=openai
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
HUGGINGFACEHUB_API_TOKEN=
HUGGINGFACE_MODEL=mistralai/Mistral-7B-Instruct-v0.2
MAX_TOKENS=512
TEMPERATURE=0.2

RATE_LIMIT_PER_MINUTE=60
ASYNC_PROCESSING=true
RQ_QUEUE_NAME=rag-jobs

MAX_UPLOAD_MB=20
ALLOWED_FILE_TYPES=pdf,docx,txt,csv

VITE_API_URL=
VITE_API_BASE_PATH=/api/v1
```

For Docker deployments, override the database and Redis hosts to service names. For Vercel, set `VITE_API_URL` to the Render backend URL and set `ALLOWED_ORIGINS` on the backend to the final frontend domain.

## Local Development

```bash
cd backend
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8011
```

```bash
cd frontend
npm install
npm run dev
```

Expected local URLs:

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8011/api/v1`
- Backend docs: `http://localhost:8011/api/v1/docs`

## Docker Workflow

```bash
cp .env.example .env
# update secrets and any production values
docker compose up --build -d
```

Expected Docker URLs:

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000/api/v1`
- Backend docs: `http://localhost:8000/api/v1/docs`

Docker runtime notes:

- `docker-compose.yml` already maps backend traffic to the internal container port `8000`.
- The frontend container proxies `/api/` to the backend service so browser calls stay on the same origin.
- The backend container uses the Docker service names for Postgres, Redis, and Chroma.

## Vercel + Render Production Workflow

### Backend on Render

Set these environment variables on the backend service:

- `ENV=production`
- `DEBUG=false`
- `SECRET_KEY=<long-random-secret>`
- `DATABASE_URL=<Render Postgres URL>`
- `REDIS_URL=<Render Redis URL>` if Redis is external
- `ALLOWED_ORIGINS=https://your-frontend.vercel.app`
- `OPENAI_API_KEY=<or your chosen provider key>`
- `HUGGINGFACEHUB_API_TOKEN=<if used>`
- `VITE_API_URL` is not used on the backend and should be left unset

Render service settings:

- Build Command: use the default Python build flow or `pip install -r backend/requirements.txt` if you are building from the repo root
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Root Directory: `backend` if the Render service is pointed at the backend subfolder

### Frontend on Vercel

Set these build-time environment variables on the frontend project:

- `VITE_API_URL=https://your-backend.onrender.com`
- `VITE_API_BASE_PATH=/api/v1`

Vercel build settings:

- Build Command: `npm run build`
- Output Directory: `dist`
- Root Directory: `frontend` if deploying from the repo root

Vercel will build the frontend against the Render backend origin, while the browser still uses `/api/v1` paths under that origin.

### Production URLs

- Frontend: `https://your-frontend.vercel.app`
- Backend API: `https://your-backend.onrender.com/api/v1`
- Backend docs: `https://your-backend.onrender.com/api/v1/docs`

## Final Production Environment Variables

Backend:

- `ENV=production`
- `DEBUG=false`
- `SECRET_KEY`
- `ALLOWED_ORIGINS`
- `DATABASE_URL` or `POSTGRES_*`
- `REDIS_URL` or `REDIS_*`
- `OPENAI_API_KEY` and/or `HUGGINGFACEHUB_API_TOKEN`
- `VECTOR_STORE`
- `CHROMA_HOST` and `CHROMA_PORT` if using self-hosted Chroma

Frontend:

- `VITE_API_URL`
- `VITE_API_BASE_PATH=/api/v1`

## Deployment Checklist

- Confirm the backend health endpoint returns `{"status":"ok"}`.
- Confirm the frontend build succeeds with the production env vars.
- Confirm `ALLOWED_ORIGINS` includes the deployed frontend URL.
- Confirm `VITE_API_URL` points at the deployed backend origin for Vercel.
- Confirm Docker deployments keep using service-name hosts internally.
- Confirm no browser requests point at `localhost` in production.
- Confirm the backend docs endpoint is reachable from the deployed backend URL.

## Scaling

- Increase worker replicas for embedding throughput.
- Scale backend service horizontally.
- Use an external vector store if required.
