# app/firebase_config.py
import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path
import os

#  Ruta absoluta al service_account.json (una carpeta arriba de /app)
SA_PATH = Path(__file__).resolve().parents[1] / "service_account.json"

if not SA_PATH.exists():
    raise FileNotFoundError(f"No se encontró el archivo: {SA_PATH}")

print(f"[FIREBASE] Cargando credenciales desde: {SA_PATH}")

#  Inicializa Firebase solo una vez
if not firebase_admin._apps:
    cred = credentials.Certificate(SA_PATH)
    firebase_admin.initialize_app(cred)
    print("[FIREBASE] App inicializada correctamente ✅")
else:
    print("[FIREBASE] Reutilizando app existente")

#  Cliente de Firestore listo
db = firestore.client()
