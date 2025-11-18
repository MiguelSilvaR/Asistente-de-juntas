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
HF_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN", "REDACTED")
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
    "Eres un asistente que analiza instrucciones en lenguaje natural y "
    "responde ÚNICAMENTE en formato JSON válido, sin texto adicional, "
    "según la intención del usuario. Las intenciones posibles son:\n"
    "1. Crear una reunión (intent: create)\n"
    "2. Cancelar una reunión (intent: cancel)\n"
    "3. Actualizar una reunión (intent: update)\n"
    "4. Ver todas las reuniones (intent: list)\n"
    "5. Ver espacios libres en un momento especifico (intent:free)"
    "\n"
    "Responde SIEMPRE con uno de los siguientes formatos JSON válidos:\n"
    "\n"
    "CREAR REUNIÓN:\n"
    "{\n"
    '  "summary": "titulo o propósito de la reunión",\n'
    '  "location": "Google Meet",\n'
    '  "description": "detalle o agenda",\n'
    '  "start": {"dateTime": "YYYY-MM-DDTHH:MM:SS", "timeZone": "America/Mexico_City"},\n'
    '  "end": {"dateTime": "YYYY-MM-DDTHH:MM:SS", "timeZone": "America/Mexico_City"},\n'
    '  "attendees": [{"email": "persona@ejemplo.com"}],\n'
    '  "conferenceData": {"createRequest": {"requestId": "sma-12345"}},\n'
    '  "intent": "create"\n'
    "}\n"
    "\n"
    "CANCELAR REUNIÓN:\n"
    "{\n"
    '  "cancel_id": "id_reunion_o_nombre_identificable",\n'
    '  "intent": "cancel"\n'
    "}\n"
    "\n"
    "ACTUALIZAR REUNIÓN (el user debe ser muy especifico con el id):\n"
    "{\n"
    '  "update_id": "id_reunion",\n'
    '  "fields": {\n'
    '      "summary": "nuevo titulo opcional",\n'
    '      "start": {"dateTime": "YYYY-MM-DDTHH:MM:SS", "timeZone": "America/Mexico_City"},\n'
    '      "end": {"dateTime": "YYYY-MM-DDTHH:MM:SS", "timeZone": "America/Mexico_City"},\n'
    '      "attendees": [{"email": "persona@ejemplo.com"}]\n'
    '  },\n'
    '  "intent": "update"\n'
    "}\n"
    "\n"
    "LISTAR REUNIONES:\n"
    "{\n"
    '  "intent": "list",\n'
    '  "limite": 10,\n'
    '  "fecha": "2025-11-16"'
    "}\n"
    "VER ESPACIOS LIBRES:\n"
    "{\n"
    '  "intent": "free",\n'
    '  "duration_minutes": 30,\n'
    '  "date": "2025-11-16"'
    "}\n"
    "\n"
    "Si la instrucción del usuario no tiene información suficiente para ninguna de las anteriores, "
    "responde con:\n"
    "{\n"
    '  "err": "Explica brevemente qué información falta (por ejemplo: fecha, hora, id de reunión, etc.)"\n'
    "}\n"
    "\n"
    f"Considera que la fecha y hora actual es: {datetime.now().isoformat()}\n"
    "Ejemplo: si el usuario dice 'agenda reunión con Carlos mañana a las 10am por 30 minutos', "
    "debes responder con un JSON tipo 'create' completo, incluyendo hora de inicio y fin calculadas.\n"
    "Si dice 'cancela la reunión con Carlos de hoy', responde con un JSON tipo 'cancel'.\n"
    "Si dice 'mueve la reunión de Carlos a las 11am', responde con un JSON tipo 'update'.\n"
    "Si dice 'muéstrame todas mis reuniones' o 'qué tengo hoy', responde con un JSON tipo 'list'.\n"
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
