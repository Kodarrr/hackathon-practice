# hackathon-practice

A minimal FastAPI application.

## Features

- `GET /health` — health check endpoint
- `POST /echo` — example request/response endpoint

## Run locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Example request

```bash
curl -X POST "http://127.0.0.1:8000/echo" \
  -H "Content-Type: application/json" \
  -d '{"message":"hello"}'
```
