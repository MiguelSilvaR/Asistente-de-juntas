# ============================================================
# Hugging Face Client — integración con Router OpenAI-style
# ============================================================

import os
import json
import requests
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# ------------------------------------------------------------
# 1️Cargar .env manualmente (sin depender de dotenv)
# ------------------------------------------------------------
ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
if ENV_PATH.exists():
    with open(ENV_PATH, "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip().strip('"').strip("'")

# ------------------------------------------------------------
# Configuración general
# ------------------------------------------------------------
HF_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN", "***REMOVED***")
HF_MODEL = os.getenv("HF_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
HF_URL = "https://router.huggingface.co/v1/chat/completions"

print("============================================================")
print(f"[HF_CLIENT] ENV_PATH        = {ENV_PATH}")
print(f"[HF_CLIENT] HF_MODEL        = {HF_MODEL}")
print(f"[HF_CLIENT] HF_URL          = {HF_URL}")
print(f"[HF_CLIENT] HF_TOKEN_SET    = {bool(HF_TOKEN)}")
print("============================================================")

# ------------------------------------------------------------
# Función principal: llamar al modelo
# ------------------------------------------------------------
def parse_create_intent(text: str) -> Dict[str, Any]:
    """
    Envía una solicitud al modelo instruct/chat para convertir
    texto libre en JSON estructurado de reunión.
    """
    if not HF_TOKEN:
        return {"__error__": "No se encontró el token de Hugging Face."}

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }

    system_prompt = (
        "Eres un asistente que analiza instrucciones en lenguaje natural "
        "y responde SOLO en formato JSON válido con la siguiente estructura SI Y SOLO SI el USUARIO desea crear una reunion y te da la suficiente informacion:\n"
        """
        {"summary","location":"Google Meet","description","start":{"dateTime","timeZone"},"end":{"dateTime","timeZone"},"attendees":[{"email"}],"conferenceData":{"createRequest":{"requestId":"sma-12345"}},intent:create}
        """
        "si desea cancelar, analiza si te da un id y devuelve un JSON CON UNICAMENTE:"
        "\{cancel_id, intent:cancel\}"
        "En caso que las instrucciones no sean claras regresa un JSON \{err\} explicando que falta"
        "Considera que la fecha de hoy es " + str(datetime.now())
    )

    payload = {
        "model": HF_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        "temperature": 0.3,
        "max_tokens": 512
    }

    try:
        res = requests.post(HF_URL, headers=headers, json=payload, timeout=90)
        if res.status_code != 200:
            return {"__error__": f"Error {res.status_code}: {res.text}"}

        data = res.json()
        message = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

        # intentar decodificar JSON del mensaje
        try:
            parsed = json.loads(message)
            return parsed
        except Exception:
            return {"raw_response": message, "__error__": "No se pudo decodificar JSON limpio."}

    except Exception as e:
        return {"__error__": str(e)}


# ------------------------------------------------------------
# Prueba directa
# ------------------------------------------------------------
if __name__ == "__main__":
    test_text = (
        "agenda mañana 16:00 por 45 min con maria@example.com y hector@example.com, "
        "tema roadmap de IA"
    )
    result = parse_create_intent(test_text)
    print("\n--- Resultado del modelo ---")
    print(json.dumps(result, indent=2, ensure_ascii=False))
