from datetime import date, datetime, time, timedelta
import os.path
from zoneinfo import ZoneInfo
import pytz

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pathlib import Path

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

#SA_PATH = Path(__file__).resolve().parents[1] / "service_account.json"

"""Shows basic usage of the Google Calendar API.
Prints the start and name of the next 10 events on the user's calendar.
"""
SA_PATH = Path(__file__).resolve().parents[1] / "calendar_service_account.json"
TOKEN_FILE = Path(__file__).resolve().parents[1] / "token.json"

def create_calendar_meeting(event):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # Si no hay token o está vencido sin refresh_token, corre el flujo
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # local server flow (abre navegador). Para “offline” y refresh_token garantizado:
            flow = InstalledAppFlow.from_client_secrets_file(SA_PATH, SCOPES)
            # En “Web app” o si no puedes abrir navegador, usa: flow.run_console()
            creds = flow.run_local_server(
                port=0,
                prompt="consent",       # fuerza pantalla de consentimiento
                access_type="offline",  # asegura refresh_token
                include_granted_scopes="true"
            )
        # Guarda token.json con token, refresh_token, client_id, client_secret, etc.
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)
        created = service.events().insert(
            calendarId="primary",
            body=event,
            conferenceDataVersion=1
        ).execute()

        return created

    except HttpError as error:
        print(f"An error occurred: {error}")

def update_calendar_meeting(event_id: str, updates: dict):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # Si no hay token o está vencido sin refresh_token, corre el flujo
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # local server flow (abre navegador). Para “offline” y refresh_token garantizado:
            flow = InstalledAppFlow.from_client_secrets_file(SA_PATH, SCOPES)
            # En “Web app” o si no puedes abrir navegador, usa: flow.run_console()
            creds = flow.run_local_server(
                port=0,
                prompt="consent",       # fuerza pantalla de consentimiento
                access_type="offline",  # asegura refresh_token
                include_granted_scopes="true"
            )
        # Guarda token.json con token, refresh_token, client_id, client_secret, etc.
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    
    try:
        service = build("calendar", "v3", credentials=creds)

        updated = service.events().patch(
            calendarId="primary",
            eventId=event_id,
            body=updates,
            conferenceDataVersion=1
        ).execute()

        return updated

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


def cancel_calendar_meeting(event_id):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # Si no hay token o está vencido sin refresh_token, corre el flujo
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # local server flow (abre navegador). Para “offline” y refresh_token garantizado:
            flow = InstalledAppFlow.from_client_secrets_file(SA_PATH, SCOPES)
            # En “Web app” o si no puedes abrir navegador, usa: flow.run_console()
            creds = flow.run_local_server(
                port=0,
                prompt="consent",       # fuerza pantalla de consentimiento
                access_type="offline",  # asegura refresh_token
                include_granted_scopes="true"
            )
        # Guarda token.json con token, refresh_token, client_id, client_secret, etc.
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)
        
        # o guarda este ID en tu BD
        service.events().delete(
            calendarId="primary",
            eventId=event_id,
            sendUpdates="all"  # envía cancelación a los invitados
        ).execute()
    except HttpError as error:
        print(f"An error occurred: {error}")

TIMEZONE = "America/Mexico_City"

def list_events_for_date(target_date: date, timezone: str = "America/Mexico_City"):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # Si no hay token o está vencido sin refresh_token, corre el flujo
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # local server flow (abre navegador). Para “offline” y refresh_token garantizado:
            flow = InstalledAppFlow.from_client_secrets_file(SA_PATH, SCOPES)
            # En “Web app” o si no puedes abrir navegador, usa: flow.run_console()
            creds = flow.run_local_server(
                port=0,
                prompt="consent",       # fuerza pantalla de consentimiento
                access_type="offline",  # asegura refresh_token
                include_granted_scopes="true"
            )
        # Guarda token.json con token, refresh_token, client_id, client_secret, etc.
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    events = []
    try:
        service = build("calendar", "v3", credentials=creds)
        # Inicio del día en la zona indicada
        start_dt = datetime.combine(target_date, datetime.min.time(), tzinfo=ZoneInfo(timezone))
        end_dt = start_dt + timedelta(days=1)

        time_min = start_dt.isoformat()  # se recomienda añadir 'Z' si usas UTC, aquí usamos TZ local lógica
        time_max = end_dt.isoformat()

        events_result = service.events().list(
            calendarId="primary",
            timeMin=time_min,
            timeMax=time_max,
            timeZone=timezone,
            singleEvents=True,
            orderBy="startTime",
        ).execute()

        events = events_result.get("items", [])
    except HttpError as error:
        print(f"An error occurred: {error}")
   
    return events

def get_calendar_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(SA_PATH, SCOPES)
            creds = flow.run_local_server(
                port=0,
                prompt="consent",
                access_type="offline",
                include_granted_scopes="true"
            )
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


def find_free_slots_for_day(date, min_slot_minutes=30):
    service = get_calendar_service()
    tz = pytz.timezone(TIMEZONE)

    # Día completo en TZ local
    start_dt = tz.localize(datetime(date.year, date.month, date.day, 0, 0, 0))
    end_dt   = start_dt + timedelta(days=1)

    body = {
        "timeMin": start_dt.isoformat(),
        "timeMax": end_dt.isoformat(),
        "timeZone": TIMEZONE,
        "items": [{"id": "primary"}],
    }

    resp = service.freebusy().query(body=body).execute()
    busy_list = resp["calendars"]["primary"]["busy"]  # lista de intervalos ocupados

    # Si no hay eventos: el día completo está libre
    if not busy_list:
        return [(start_dt, end_dt)]

    free_slots = []
    current_start = start_dt

    for interval in busy_list:
        busy_start = datetime.fromisoformat(interval["start"])
        busy_end   = datetime.fromisoformat(interval["end"])

        if busy_start > current_start:
            gap = busy_start - current_start
            if gap.total_seconds() >= min_slot_minutes * 60:
                free_slots.append((current_start, busy_start))

        # mueve el cursor al final del evento ocupado
        if busy_end > current_start:
            current_start = busy_end

    # hueco al final del día
    if current_start < end_dt:
        gap = end_dt - current_start
        if gap.total_seconds() >= min_slot_minutes * 60:
            free_slots.append((current_start, end_dt))

    return free_slots


def chunk_slots(start: datetime, end: datetime, duration_minutes: int):
    """Divide un hueco [start, end] en slots contiguos de duración fija."""
    slots = []
    delta = timedelta(minutes=duration_minutes)
    cursor = start
    while cursor + delta <= end:
        slots.append((cursor, cursor + delta))
        cursor += delta
    return slots
