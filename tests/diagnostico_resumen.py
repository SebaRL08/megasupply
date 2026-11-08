"""Mide velocidad y calidad de cada modelo. Ejecutar: python -m tests.diagnostico_resumen [modelo1,modelo2]"""
import json
import os
import sys
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
from src.infrastructure.gemini_report_writer import SYSTEM  # noqa: E402

DATA = {
    "periodo": "2026-11",
    "mas_demandados": [{"codigo": "PROD-001", "producto": "Tela Algodón", "unidades": 90, "salidas": 9}],
    "por_agotarse": [{"codigo": "PROD-003", "en_cajon": 5, "minimo": 25, "en_cajas": 10}],
    "pedidos_pendientes": 1,
    "recomendaciones_pendientes": [{"codigo": "PROD-001", "sugerida": 90, "riesgo": "ALTO", "datos_base": "simulado"}],
}
PROMPT = "Datos del mes (JSON):\n" + json.dumps(DATA, ensure_ascii=False)

key = os.getenv("GEMINI_API_KEY")
if not key:
    raise SystemExit("Falta GEMINI_API_KEY en .env")
raw = sys.argv[1] if len(sys.argv) > 1 else os.getenv("GEMINI_MODELS", "gemini-3.5-flash-lite,gemini-3.8-flash")
client = genai.Client(api_key=key, http_options=types.HttpOptions(timeout=60000))
config = types.GenerateContentConfig(system_instruction=SYSTEM, temperature=0.3, max_output_tokens=4096)

for model in [m.strip() for m in raw.split(",") if m.strip()]:
    print(f"\n=== {model} ===")
    start = time.time()
    try:
        r = client.models.generate_content(model=model, contents=PROMPT, config=config)
        u = r.usage_metadata
        print(f"Tiempo: {time.time() - start:.1f} s | fin: {r.candidates[0].finish_reason} | "
              f"tokens de salida: {getattr(u, 'candidates_token_count', '?')} | "
              f"tokens pensando: {getattr(u, 'thoughts_token_count', '?')}")
        text = (r.text or "").strip()
        print(f"Palabras: {len(text.split())}\n{text[:600]}")
    except Exception as exc:
        print(f"ERROR tras {time.time() - start:.1f} s: {str(exc).replace(key, '***')[:300]}")
    