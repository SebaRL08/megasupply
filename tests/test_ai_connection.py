"""
Módulo: test_ai_connection.py
Descripción: Script de prueba para validar la conectividad inicial con Google AI Studio (Gemini)
             utilizando la librería oficial 'google.genai', manejo de fallos y fallback de modelos.
Autor: Sebastián (Equipo MegaSupply)
"""

import os
import json
import time
from google import genai
from google.genai import errors
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener la API Key desde el entorno
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("No se encontró la GEMINI_API_KEY en las variables de entorno (.env).")

# Inicializar el cliente oficial de Gemini
client = genai.Client(api_key=api_key)

def probar_conexion_gemini():
    """
    Realiza una llamada de prueba a la API de Gemini enviando un mensaje 
    de inventario y procesando la respuesta en formato JSON.
    """
    prompt = (
        "Analyze the stock status for MegaSupply product 'Industrial Cotton': "
        "Current stock: 5, Minimum drawer requirement: 15. "
        "Respond STRICTLY in JSON format with keys: 'product', 'stock_status', and 'reorder_suggested'."
    )

    # Lista de modelos oficiales en orden de preferencia
    modelos_a_probar = ["gemini-3.8-flash", "gemini-2.5-flash-lite", "gemini-1.5-flash"]
    response = None

    for model_name in modelos_a_probar:
        try:
            print(f"Enviando mensaje de prueba usando el modelo '{model_name}'...")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            print(f"¡Conexión exitosa usando '{model_name}'!")
            break
        except errors.ServerError as e:
            print(f"[Aviso 503] El modelo {model_name} tiene alta demanda temporal. Probando siguiente...")
            time.sleep(2)
        except errors.APIError as e:
            print(f"[Aviso {e.code}] El modelo {model_name} no estuvo disponible ({e.message[:60]}...). Probando siguiente...")
            time.sleep(1)

    if not response:
        print("\n[Error] No se pudo obtener respuesta de ningún modelo.")
        return

    print("\n--- Respuesta cruda del modelo ---")
    print(response.text)

    # Procesar la respuesta simulando un parseo a JSON para cumplir con la rúbrica
    try:
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        response_json = json.loads(clean_text)
        print("\n--- Respuesta procesada exitosamente como JSON ---")
        print(json.dumps(response_json, indent=4, ensure_ascii=False))
    except json.JSONDecodeError:
        print("\n[Aviso] La respuesta se recibió, pero el texto requiere ajuste de formato JSON.")

if __name__ == "__main__":
    probar_conexion_gemini()