import os.path

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

