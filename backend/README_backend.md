# 🧠 Asistente de Juntas — Backend

Backend desarrollado en **FastAPI** que se conecta con **Firebase Firestore** y un modelo de lenguaje de **Hugging Face**, para generar y administrar juntas de manera inteligente a partir de texto libre.

---

## 🚀 Características principales

- Creación automática de reuniones a partir de texto (ejemplo:  
  _“Agendar junta mañana a las 16:00 con María y Héctor sobre el roadmap”_).
- Almacenamiento de reuniones en **Firebase Firestore**.
- Integración con **modelos de lenguaje (LLMs)** a través de la API de Hugging Face.
- API REST documentada automáticamente con Swagger (disponible en `/docs`).
- Arquitectura modular lista para conectar con un frontend en React + Vite.

---

## ⚙️ Configuración del entorno

### 1️⃣ Crear entorno virtual
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 2️⃣ Instalar dependencias
```bash
pip install -r requirements.txt
```

---

## 🔧 Configuración del archivo `.env`

El proyecto utiliza variables de entorno para proteger credenciales y configurar servicios externos como Firebase y Hugging Face.  
Estas variables se almacenan en un archivo llamado `.env`, el cual **no debe subirse a GitHub** por motivos de seguridad.

### 📄 Ejemplo de `.env`
Crea un archivo `.env` en la carpeta `backend/` con el siguiente contenido:

```bash
# === Configuración de Hugging Face ===
HUGGINGFACE_API_TOKEN=hf_tu_token_aqui
HF_MODEL=meta-llama/llama-3.1-8b-instruct

# === Configuración local ===
APP_ENV=development
TIMEZONE=America/Matamoros

# === Configuración de Firebase ===
GOOGLE_APPLICATION_CREDENTIALS=service_account.json
```

---

### 🔍 Descripción de las variables

| Variable | Descripción |
|-----------|--------------|
| `HUGGINGFACE_API_TOKEN` | Token personal generado desde tu cuenta de [Hugging Face](https://huggingface.co/settings/tokens). Permite acceder a modelos alojados en su API. |
| `HF_MODEL` | Nombre del modelo que se usará para interpretar y generar texto (por ejemplo, `google/flan-t5-base` o `meta-llama/llama-3.1-8b-instruct`). |
| `APP_ENV` | Define el entorno de ejecución (`development`, `staging`, `production`). |
| `TIMEZONE` | Zona horaria usada para las reuniones y cálculos de tiempo. |
| `GOOGLE_APPLICATION_CREDENTIALS` | Archivo JSON con las credenciales del servicio de Firebase (debe estar ubicado en `backend/` y nunca subirse al repositorio). |

---

## 🔑 Cómo generar tu token de Hugging Face

1. Crea o inicia sesión en tu cuenta en [https://huggingface.co](https://huggingface.co).
2. Abre el menú de tu perfil → selecciona **Settings** → **Access Tokens**.
3. Haz clic en **New Token**.
4. Asigna un nombre descriptivo, selecciona **Read** como permiso.
5. Copia el token generado (empieza con `hf_...`).
6. Pega el token en tu archivo `.env` en la línea:
   ```bash
   HUGGINGFACE_API_TOKEN=hf_tu_token_aqui
   ```
7. Guarda los cambios y reinicia el servidor FastAPI.

---

## 🧩 Ejecución del backend

### Iniciar servidor local
```bash
uvicorn app.main:app --reload
```

### Ver documentación interactiva (Swagger UI)
👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---
🛠️ Setup
Crear y activar virtualenv
cd backend
python -m venv .venv
.\.venv\Scripts\activate
Instalar dependencias
pip install -r requirements.txt
Colocar credenciales Firebase
Guardar service_account.json en backend/service_account.json.

Configurar .env
Crear backend/.env con las variables anteriores.



---

## 🧠 Ejemplo de uso

### Crear una reunión mediante texto
`POST /v1/meetings/create_from_text`

**Ejemplo de body JSON:**
```json
{
  "text": "Agenda reunión mañana a las 16:00 con maria@example.com y hector@example.com sobre roadmap"
}
```

**Respuesta esperada:**
```json
{
  "ok": true,
  "meeting": {
    "title": "Reunión sobre roadmap",
    "start": "2025-11-10T16:00:00",
    "end": "2025-11-10T16:45:00",
    "attendees": ["maria@example.com", "hector@example.com"],
    "agenda": "roadmap",
    "timezone": "America/Matamoros",
    "status": "created"
  }
}
```

---

## 📂 Estructura del backend

```
backend/
├── app/
│   ├── main.py               # Lógica principal de FastAPI
│   ├── firebase_config.py    # Conexión a Firebase Firestore
│   ├── hf_client.py          # Cliente para modelos de Hugging Face
│   ├── __init__.py
├── requirements.txt
├── README.md
├── .gitignore
└── .env (no subir)
```

---

## 🧱 Stack tecnológico

- **FastAPI** — Framework backend asíncrono moderno
- **Firebase Admin SDK** — Conexión a Firestore
- **Hugging Face Inference API** — Modelos LLM (Flan-T5, Llama 3, etc.)
- **Python-Dotenv** — Carga de variables de entorno
- **Uvicorn** — Servidor ASGI de desarrollo
