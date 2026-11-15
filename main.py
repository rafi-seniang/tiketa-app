"""Entry point. `python main.py` for a local run with reload, or
`uvicorn main:app --port 8070` (on Windows add `--loop asyncio:SelectorEventLoop`, which psycopg needs)."""

import uvicorn

from app.core.application import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8070, reload=True, loop="asyncio:SelectorEventLoop")
