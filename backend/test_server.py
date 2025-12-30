#!/usr/bin/env python
"""Minimal FastAPI test to verify uvicorn works"""
import sys
print(f"Starting test server...", flush=True)

from fastapi import FastAPI

print(f"FastAPI imported successfully", flush=True)

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    print(f"Starting uvicorn...", flush=True)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8011, log_level="info")
