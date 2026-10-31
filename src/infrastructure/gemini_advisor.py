import os, json
from google import genai

class GeminiAdvisor:
    def __init__(self, model: str = "gemini-3.8-flash"):  # mismo modelo que ya usas
        self._client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self._model = model

    def advise(self, question: str) -> dict:
        r = self._client.models.generate_content(
            model=self._model, contents=question + "\nRespond STRICTLY in JSON.")
        return json.loads(r.text.replace("```json", "").replace("```", "").strip())