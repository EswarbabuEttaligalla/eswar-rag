# API Documentation

Base URL: /api/v1

## Auth
- POST /auth/register
- POST /auth/login
- POST /auth/refresh
- POST /auth/logout

## Users
- GET /users/me
- GET /users (admin)

## Documents
- POST /documents/upload
- GET /documents
- POST /documents/{document_id}/process
- DELETE /documents/{document_id}

## RAG
- POST /rag/query

## Chat
- POST /chat
- GET /chat
- GET /chat/{chat_id}/messages
- POST /chat/{chat_id}/messages
- POST /chat/{chat_id}/ask
- POST /chat/{chat_id}/ask/stream

## Analytics
- GET /analytics/overview (admin)

## Health
- GET /health
