from __future__ import annotations

import asyncio
import os
import sys
import time

backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from app.core.events import lifespan
from app.main import app


async def main() -> None:
    print("probe: entering lifespan", flush=True)
    cm = lifespan(app)
    started = time.monotonic()
    try:
        await asyncio.wait_for(cm.__aenter__(), timeout=20)
        print(f"probe: lifespan entered in {time.monotonic() - started:.2f}s", flush=True)
    except Exception as exc:
        print(f"probe: lifespan enter failed after {time.monotonic() - started:.2f}s: {type(exc).__name__}: {exc}", flush=True)
        raise
    try:
        await cm.__aexit__(None, None, None)
        print("probe: lifespan exited", flush=True)
    except Exception as exc:
        print(f"probe: lifespan exit failed: {type(exc).__name__}: {exc}", flush=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
