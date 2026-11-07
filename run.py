"""Arranca la API en segundo plano y abre la interfaz. Ejecutar: python run.py"""
import threading
import time

import httpx
import uvicorn
from dotenv import load_dotenv

load_dotenv()
from src.api.main import app  # noqa: E402


def start_api():
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="warning"))
    threading.Thread(target=server.run, daemon=True).start()
    for _ in range(40):
        try:
            if httpx.get("http://127.0.0.1:8000/health", timeout=1).status_code == 200:
                return
        except httpx.HTTPError:
            time.sleep(0.25)
    raise SystemExit("La API no arrancó. Revisa PostgreSQL y el archivo .env")


if __name__ == "__main__":
    start_api()
    from src.ui.main_window import run_ui
    run_ui()
    