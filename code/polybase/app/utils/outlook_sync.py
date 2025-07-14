# ============================================
# IMPORTS
# ============================================

import os
from datetime import datetime, timedelta
from os import getenv
from urllib.parse import urlencode

import msal
import requests
from dotenv import load_dotenv
from sqlalchemy import text

from app.database import SessionLocal
from app.models import Tache

# ============================================
# LOADING .ENV
# ============================================

load_dotenv()

CLIENT_ID = os.getenv("GRAPH_CLIENT_ID")
TENANT_ID = os.getenv("GRAPH_TENANT_ID")
CLIENT_SECRET = os.getenv("GRAPH_CLIENT_SECRET")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://graph.microsoft.com/.default"]
REDIRECT_URI = "http://localhost:8000/outlook/callback"
OAUTH_SCOPE = ["Calendars.ReadWrite"]

# ============================================
# SYNCHRONISATION FUNCTIONS
# ============================================

def get_token():
    """Gets a valid OAuth2 access token via MSAL for the Graph API.
    Returns:
    --------
    str | None: OAuth2 access token or None if unsuccessful.
    Version:
    --------
    specification: Esteban Barracho (v.2 11/07/2025)
    implement: Esteban Barracho (v.2 11/07/2025)
    """
    assert CLIENT_ID and CLIENT_SECRET and TENANT_ID, "Variables d'environnement Outlook manquantes"
    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET
    )
    result = app.acquire_token_for_client(scopes=SCOPE)
    return result.get("access_token")

def fetch_outlook_events(access_token):
    """Retrieves Outlook events scheduled for the next 30 days.
    Parameters:
    -----------
    access_token: str
        Valid OAuth2 token for authentication.
    Returns:
    --------
    list[dict]: List of events extracted from Microsoft Graph.
    Version:
    --------
    specification: Esteban Barracho (v.2 11/07/2025)
    implement: Esteban Barracho (v.2 11/07/2025)
    """
    assert isinstance(access_token, str) and len(access_token) > 10, "Token OAuth2 invalide"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    today = datetime.utcnow().isoformat()
    future = (datetime.utcnow() + timedelta(days=30)).isoformat()
    url = f"https://graph.microsoft.com/v1.0/me/calendarview?startdatetime={today}&enddatetime={future}"
    response = requests.get(url, headers=headers)
    assert response.status_code == 200, f"Erreur lors de la récupération des événements Outlook: {response.status_code}"
    return response.json().get("value", [])

def sync_to_db(events):
    """Inserts Outlook events into PlanificationCollaborateur, without duplicates.
    Parameters:
    -----------
    events: list[dict]
        List of events retrieved from Outlook.

    Version:
    --------
    specification: Esteban Barracho (v.2 11/07/2025)
    implement: Esteban Barracho (v.2 11/07/2025)
    """
    assert isinstance(events, list), "Événements Outlook mal formatés (liste attendue)"
    db = SessionLocal()
    try:
        for ev in events:
            assert isinstance(ev, dict), "Événement Outlook invalide"
            sujet = ev.get("subject", "Sans titre")
            date_debut = ev.get("start", {}).get("dateTime", "")
            date_fin = ev.get("end", {}).get("dateTime", "")
            if not date_debut or not date_fin:
                continue
            date_debut = date_debut[:19]
            date_fin = date_fin[:19]
            exists = db.execute(text("""
                                     SELECT 1
                                     FROM PlanificationCollaborateur
                                     WHERE sujet = :s
                                       AND date_debut = :d1
                                       AND date_fin = :d2
                                     """), {"s": sujet, "d1": date_debut, "d2": date_fin}).first()
            if exists:
                continue
            db.execute(text("""
                            INSERT INTO PlanificationCollaborateur (sujet, date_debut, date_fin, source)
                            VALUES (:s, :d1, :d2, 'outlook')
                            """), {"s": sujet, "d1": date_debut, "d2": date_fin})
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"❌ Erreur de sync Outlook: {e}")
    finally:
        db.close()

def launch_sync():
    """Launches full synchronization from Outlook to the database.
    This function performs the following steps:
    Retrieves the client token,
    Extracts Outlook events,
    Inserts filtered events into the database.
    Version:
    --------
    specification: Esteban Barracho (v.2 11/07/2025)
    implement: Esteban Barracho (v.2 11/07/2025)
    """
    try:
        token = get_token()
        events = fetch_outlook_events(token)
        sync_to_db(events)
        print(f"✔ Outlook sync terminé : {len(events)} événements analysés.")
    except Exception as e:
        print(f"❌ Outlook sync échouée: {e}")

def synchronize_outlook():
    """Main entry point called when the backend starts up.
    This function triggers the retrieval of Outlook events
    and their insertion into the database, if necessary.
    Version:
    --------
    specification: Esteban Barracho (v.2 11/07/2025)
    implement: Esteban Barracho (v.2 11/07/2025)
    """
    if not all([getenv("GRAPH_CLIENT_ID"), getenv("GRAPH_TENANT_ID"), getenv("GRAPH_CLIENT_SECRET")]):
        print("⚠️  Identifiants Outlook manquants, synchronisation ignorée.")
        return
    print("🔄 Synchronisation Outlook en cours...")
    launch_sync()

def get_oauth_url():
    """Dynamically builds the redirect URL for OAuth2 authentication.
    Returns:
    --------
    str: Microsoft OAuth2 authorisation URL to open in a browser.
    Version:
    --------
    specification: Esteban Barracho (v.2 11/07/2025)
    implement: Esteban Barracho (v.2 11/07/2025)
    """
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "response_mode": "query",
        "scope": " ".join(OAUTH_SCOPE),
    }
    return f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize?{urlencode(params)}"

def exchange_code_for_token(code: str):
    """Exchange an authorisation code for an OAuth2 access token.
    Parameters:
    -----------
    code: str
        Code returned after user authorisation.
    Returns:
    --------
    str | None: OAuth2 access token or None if error.
    Version:
    --------
    specification: Esteban Barracho (v.2 11/07/2025)
    implement: Esteban Barracho (v.2 11/07/2025)
    """
    assert isinstance(code, str) and code.strip(), "Code d'autorisation invalide ou manquant"
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    data = {
        "client_id": CLIENT_ID,
        "scope": " ".join(OAUTH_SCOPE),
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
        "client_secret": CLIENT_SECRET
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    res = requests.post(url, data=data, headers=headers)
    token = res.json().get("access_token")
    assert isinstance(token, str) and len(token) > 10, "Échec de récupération du token OAuth2"
    return token

def create_events_from_db(db, token: str):
    """Creates events in Outlook based on important system tasks.
    Parameters:
    -----------
    db: Session
        Active SQLAlchemy session.
    token: str
        Valid access token for Microsoft Graph.
    Returns:
    --------
    int: Number of events successfully created.
    Version:
    --------
    specification: Esteban Barracho (v.2 11/07/2025)
    implement: Esteban Barracho (v.2 11/07/2025)
    """
    assert db, "Session DB invalide"
    assert isinstance(token, str) and len(token) > 10, "Token OAuth2 invalide"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    taches = db.query(Tache).filter(Tache.est_realisable == 1).limit(5).all()
    count = 0
    for t in taches:
        assert t.date_debut and t.date_fin, f"Tâche {t.nom_tache} sans date"
        payload = {
            "subject": t.nom_tache,
            "start": {
                "dateTime": t.date_debut.strftime("%Y-%m-%dT%H:%M:%S"),
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": t.date_fin.strftime("%Y-%m-%dT%H:%M:%S"),
                "timeZone": "UTC"
            },
            "body": {
                "contentType": "Text",
                "content": t.description or "Tâche PolyBase"
            }
        }
        res = requests.post("https://graph.microsoft.com/v1.0/me/events", json=payload, headers=headers)
        if res.status_code in [200, 201]:
            count += 1
    return count
