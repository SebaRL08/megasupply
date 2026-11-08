"""Diagnóstico manual de Gemini. Ejecutar: python -m tests.diagnostico_gemini"""
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()
key = os.getenv("GEMINI_API_KEY")
print("Llave configurada:", bool(key), "| longitud:", len(key or ""))
if not key:
    raise SystemExit("Falta GEMINI_API_KEY en .env")
client = genai.Client(api_key=key)

print("\nModelos disponibles para tu llave (generateContent):")
try:
    names = [m.name.replace("models/", "") for m in client.models.list()
             if "generateContent" in (getattr(m, "supported_actions", None) or [])]
    for n in sorted(names):
        print("  ", n)
except Exception as exc:
    print("No se pudo listar los modelos:", str(exc).replace(key, "***")[:300])

print("\nPrueba de cada modelo configurado:")
configured = os.getenv("GEMINI_MODELS", "gemini-3.8-flash,gemini-2.5-flash-lite")
for model in [m.strip() for m in configured.split(",") if m.strip()]:
    try:
        r = client.models.generate_content(model=model, contents="Responde solo: OK")
        print(f"  {model}: OK -> {(r.text or '').strip()[:40]!r}")
    except Exception as exc:
        print(f"  {model}: ERROR -> {str(exc).replace(key, '***')[:200]}")
