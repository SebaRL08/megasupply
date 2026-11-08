"""Adaptador de Gemini para el resumen mensual. Sin historial: cada llamada es independiente."""
import json
import os
import time

from google import genai
from google.genai import types

DEFAULT_MODELS = "gemini-3.8-flash,gemini-2.5-flash-lite"
SYSTEM = ("Eres un analista de inventario. Redacta en español un resumen mensual claro y breve "
          "(máximo 250 palabras) con: panorama general, productos de mayor demanda, riesgos de "
          "desabastecimiento y acciones sugeridas. Usa únicamente los datos entregados y no inventes cifras. "
          "Si los datos base son simulados, dilo. Responde en texto plano, sin markdown.")


class GeminiReportWriter:
    def __init__(self, models: str | None = None, retries: int = 2):
        raw = models or os.getenv("GEMINI_MODELS", DEFAULT_MODELS)
        self._models = [m.strip() for m in raw.split(",") if m.strip()]
        self._retries = retries
        self.last_model: str | None = None

    def write(self, data: dict) -> str:
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("GEMINI_API_KEY is not configured")
        client = genai.Client(api_key=key)  # cliente nuevo: no se comparte estado entre llamadas
        system = SYSTEM
        context = os.getenv("REPORT_CONTEXT", "").strip()
        if context:  # contexto de empresa opcional, para más adelante
            system += f" Contexto: {context}"
        config = types.GenerateContentConfig(system_instruction=system, temperature=0.3, max_output_tokens=700)
        prompt = "Datos del mes (JSON):\n" + json.dumps(data, ensure_ascii=False)
        last: Exception | None = None
        for model in self._models:          # si un modelo falla, prueba el siguiente
            for attempt in range(self._retries):
                try:
                    text = (client.models.generate_content(model=model, contents=prompt, config=config).text or "").strip()
                    if text:
                        self.last_model = model
                        return text
                except Exception as exc:
                    last = exc
                    time.sleep(0.5 * 2 ** attempt)  # espera exponencial
        raise RuntimeError(f"AI unavailable: {last}")
