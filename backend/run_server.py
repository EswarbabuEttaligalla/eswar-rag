#!/usr/bin/env python
import sys
import os

# Add current directory to path so 'app' module is importable
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

def mark(message: str) -> None:
    log_path = os.path.join(backend_dir, "server_boot.log")
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")
        log_file.flush()


mark("before import uvicorn")
import uvicorn
mark("before import app.main")
from app.main import app
mark("after import app.main")

if __name__ == "__main__":
    mark("before uvicorn.run")
    uvicorn.run(app, host="0.0.0.0", port=8011, reload=False, log_level="info")
