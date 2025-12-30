#!/usr/bin/env python
"""Diagnose where app.main startup is hanging"""
import sys
import os

backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

print("Step 1: Importing config...", flush=True)
from app.core.config import settings
print(f"  DB Host: {settings.POSTGRES_HOST}", flush=True)

print("Step 2: Importing FastAPI...", flush=True)
from fastapi import FastAPI
print("  OK", flush=True)

print("Step 3: Importing app.main...", flush=True)
try:
    from app.main import app
    print("  OK - app.main imported successfully", flush=True)
except Exception as e:
    print(f"  ERROR: {e}", flush=True)
    import traceback
    traceback.print_exc()

print("Done!", flush=True)
