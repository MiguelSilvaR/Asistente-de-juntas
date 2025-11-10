from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from firebase_admin import firestore as fb_fs
from app.firebase_config import db
from app.hf_client import parse_create_intent

# ============================================================
# CONFIGURACIÓN BÁSICA
# ============================================================
app = FastAPI(title="Asistente de Juntas API", version="0.4")



# --- CORS (para permitir llamadas desde el frontend) ---
import os
from fastapi.middleware.cors import CORSMiddleware

# Puedes controlar orígenes por variable de entorno (coma-separados)
_frontend_origins = os.getenv(
    "FRONTEND_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173"
)

ALLOWED_ORIGINS = [o.strip() for o in _frontend_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,   # Orígenes permitidos
    allow_credentials=True,          # Cookies/Auth si llegas a usarlos
    allow_methods=["*"],             # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],             # Headers personalizados (Authorization, etc.)
    expose_headers=["*"],            # (opcional) Habilita lectura de headers de respuesta
)


# ============================================================
# MODELOS DE REUNIONES
# ============================================================
class MeetingCreate(BaseModel):
    title: str = Field(..., description="Título de la reunión")
    date: Optional[str] = Field(None, description="YYYY-MM-DD")
    start_time: Optional[str] = Field(None, description="HH:MM (24h)")
    duration_min: int = Field(30, ge=5, le=480, description="Duración en minutos")
    attendees: List[EmailStr] = Field(default_factory=list, description="Correos de asistentes")
    agenda: Optional[str] = ""
    timezone: str = Field("America/Matamoros", description="Zona horaria")


class MeetingOut(BaseModel):
    id: str
    title: str
    start: str
    end: str
    duration_min: int
    attendees: List[EmailStr]
    agenda: str
    timezone: str
    status: str
    created_at: str


# ============================================================
# MODELOS DE ACCIONES (NUEVA TABLA)
# ============================================================
class ActionLogCreate(BaseModel):
    action: str = Field(..., description="create | cancel", pattern="^(create|cancel)$")
    action_id: str = Field(..., description="Id del recurso afectado (p.ej. meeting id)")
    user: EmailStr = Field(..., description="Usuario que ejecuta la acción")
    date: Optional[str] = Field(None, description="Fecha en ISO8601 opcional")


class ActionLogOut(BaseModel):
    id: str
    action: str
    action_id: str
    user: EmailStr
    date: str


# ============================================================
# HELPERS
# ============================================================
def _combine_iso(date: Optional[str], time: Optional[str]) -> str:
    """Combina YYYY-MM-DD + HH:MM en ISO. Si falta, usa now()."""
    if date and time:
        return f"{date}T{time}:00"
    return datetime.now().replace(microsecond=0).isoformat()


def log_action(action: str, action_id: str, user: str, date_iso: Optional[str] = None) -> Dict[str, Any]:
    """Guarda una acción (create/cancel) en la colección 'actions'."""
    doc = {
        "action": action,
        "action_id": action_id,
        "user": user,
        "date": fb_fs.SERVER_TIMESTAMP if not date_iso else datetime.fromisoformat(date_iso)
    }
    ref = db.collection("actions").document()
    ref.set(doc)
    saved = ref.get().to_dict()
    saved["id"] = ref.id
    d = saved.get("date")
    saved["date"] = d.isoformat(timespec="seconds") if isinstance(d, datetime) else str(d)
    return saved


# ============================================================
# ENDPOINTS PRINCIPALES
# ============================================================
@app.get("/")
def root():
    return {"message": "API funcionando 🚀"}


@app.get("/v1/meetings", response_model=List[MeetingOut])
def list_meetings():
    docs = db.collection("meetings").order_by("created_at").stream()
    out = []
    for d in docs:
        data = d.to_dict()
        data["id"] = d.id
        out.append(data)
    return out


@app.post("/v1/meetings/create", response_model=Dict[str, Any])
def create_meeting(body: MeetingCreate):
    start_iso = _combine_iso(body.date, body.start_time)
    try:
        end_iso = (datetime.fromisoformat(start_iso) + timedelta(minutes=body.duration_min)).isoformat()
    except Exception:
        raise HTTPException(400, "Fecha u hora inválida, usa YYYY-MM-DD y HH:MM")

    doc = {
        "title": body.title,
        "start": start_iso,
        "end": end_iso,
        "duration_min": body.duration_min,
        "attendees": body.attendees,
        "agenda": body.agenda or "",
        "timezone": body.timezone,
        "status": "created",
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }

    ref = db.collection("meetings").document()
    ref.set(doc)
    doc["id"] = ref.id

    # 🔹 Registrar acción CREATE
    actor = (doc.get("attendees") or ["system@local"])[0]
    log_action("create", doc["id"], actor)

    return {"ok": True, "meeting": doc}


@app.post("/v1/meetings/{meeting_id}/cancel")
def cancel_meeting(meeting_id: str, body: ActionLogCreate):
    ref = db.collection("meetings").document(meeting_id)
    snap = ref.get()
    if not snap.exists:
        raise HTTPException(status_code=404, detail="Meeting not found")

    ref.update({
        "status": "canceled",
        "canceled_at": fb_fs.SERVER_TIMESTAMP
    })

    # 🔹 Registrar acción CANCEL
    log_action("cancel", meeting_id, body.user)

    updated = ref.get().to_dict()
    updated["id"] = meeting_id
    for k in ("created_at", "start", "end", "canceled_at"):
        v = updated.get(k)
        if isinstance(v, datetime):
            updated[k] = v.isoformat(timespec="seconds")
    return {"ok": True, "meeting": updated}


@app.get("/v1/actions", response_model=List[ActionLogOut])
def list_actions(limit: int = 50):
    docs = db.collection("actions").order_by("date", direction=fb_fs.Query.DESCENDING).limit(limit).stream()
    out = []
    for d in docs:
        data = d.to_dict()
        data["id"] = d.id
        dt = data.get("date")
        if isinstance(dt, datetime):
            data["date"] = dt.isoformat(timespec="seconds")
        out.append(data)
    return out


# ============================================================
# ENDPOINTS CON HUGGING FACE (CREACIÓN AUTOMÁTICA)
# ============================================================
class IntentIn(BaseModel):
    text: str
    default_timezone: Optional[str] = "America/Matamoros"


@app.post("/v1/intent/create/parse")
def intent_create_parse(payload: IntentIn):
    """Convierte texto libre a JSON de reunión usando el modelo HF."""
    data = parse_create_intent(payload.text)
    if "__error__" in data:
        raise HTTPException(status_code=502, detail=data["__error__"])
    if "timezone" not in data or not data["timezone"]:
        data["timezone"] = payload.default_timezone or "America/Matamoros"
    return {"intent": data}


@app.post("/v1/meetings/create_from_text")
def create_meeting_from_text(payload: IntentIn):
    """
    Parsear texto natural con LLM y crear reunión directamente.
    Ej: 'agenda mañana 16:00 por 45 min con maria@x.com y hector@y.com, tema roadmap'
    """
    intent = parse_create_intent(payload.text)
    if "title" not in intent or not intent["title"]:
        return {"ok": False, "error": "No se detectó 'title' en el texto."}

    tz = intent.get("timezone") or payload.default_timezone or "America/Matamoros"
    date = intent.get("date")
    start_time = intent.get("start_time")
    duration_min = int(intent.get("duration_min", 30))
    attendees = intent.get("attendees", [])
    agenda = intent.get("agenda", "")

    start_iso = _combine_iso(date, start_time)
    end_iso = (datetime.fromisoformat(start_iso) + timedelta(minutes=duration_min)).isoformat()

    doc = {
        "title": intent["title"],
        "start": start_iso,
        "end": end_iso,
        "duration_min": duration_min,
        "attendees": attendees,
        "agenda": agenda,
        "timezone": tz,
        "status": "created",
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }

    ref = db.collection("meetings").document()
    ref.set(doc)
    doc["id"] = ref.id

    # Registrar acción CREATE (automática)
    actor = (doc.get("attendees") or ["system@local"])[0]
    log_action("create", doc["id"], actor)

    return {"ok": True, "meeting": doc, "intent": intent}
