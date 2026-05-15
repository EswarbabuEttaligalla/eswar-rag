# Private Knowledge Assistant

Enterprise-grade retrieval augmented generation for resume and document workflows.
## Deployed Link
Live : https://eswar-rag.vercel.app/login

## Architecture Overview

The backend is a FastAPI service that handles authentication, document ingestion, retrieval, and chat orchestration. The frontend is a Vite React app that talks to the backend through `/api/v1` in local and Docker environments, and through an absolute backend origin in production. Optional infrastructure includes PostgreSQL, Redis, and Chroma for persistence, caching, and vector search.

## Feature Summary

- Document upload and chunking pipeline
- Hybrid retrieval and reranking
- Chat and message history management
- Auth, refresh tokens, and protected routes
- Analytics and evaluation support
- Dockerized local development and deployment

## Project Structure

- `backend/` FastAPI app, services, models, migrations, and workers
- `frontend/` React UI, API clients, routing, and presentation components
- `docs/` deployment and operational guidance
- `data/` local storage for uploads, vectors, and Chroma state

## Local Setup

Backend:

```bash
cd backend
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8011
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Expected local URLs:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8011/api/v1
- API docs: http://localhost:8011/api/v1/docs

## Docker Setup

```bash
cp .env.example .env
docker compose up --build
```

Expected Docker URLs:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/v1
- API docs: http://localhost:8000/api/v1/docs

## Environment Variables

See [.env.example](.env.example) for the canonical template.

- `SECRET_KEY` required for JWT signing and session security
- `DATABASE_URL` or `POSTGRES_*` for database connectivity
- `REDIS_URL` or `REDIS_*` for cache and queue support
- `ALLOWED_ORIGINS` for local and deployed frontend domains
- `VITE_API_URL` for production frontend builds that target a hosted backend
- `VITE_API_BASE_PATH` for API route prefixing
- `OPENAI_API_KEY` or `HUGGINGFACEHUB_API_TOKEN` for LLM access

## API Overview

- `GET /api/v1/health` health check
- `POST /api/v1/auth/*` authentication and token refresh
- `GET /api/v1/users/*` user operations
- `POST /api/v1/documents/*` document ingestion and retrieval setup
- `POST /api/v1/chat/*` chat and conversation endpoints
- `POST /api/v1/rag/*` retrieval and answer generation
- `GET /api/v1/analytics/*` usage and evaluation endpoints

## Deployment

The recommended production workflow is documented in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md). It covers local parity, Docker runtime behavior, Vercel frontend deployment, Render backend deployment, and the final production environment variables.

## Screenshots

Add project screenshots here after capturing the main product views.

- Landing or login screen
- Document upload or dashboard view
- Chat and retrieval response view
- Analytics or evaluation view

## Production Workflow Summary

1. Deploy the backend to Render with production secrets, database, Redis, and `ALLOWED_ORIGINS` configured.
2. Deploy the frontend to Vercel with `VITE_API_URL` pointing at the Render backend.
3. Verify the backend health endpoint and the frontend production build.
4. Confirm browser requests resolve against the deployed backend, not `localhost`.
