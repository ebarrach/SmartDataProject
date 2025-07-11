# ============================================
# IMPORTS
# ============================================

import os
import msal
import requests
from datetime import datetime, timedelta
from app.database import SessionLocal
from sqlalchemy import text
from dotenv import load_dotenv
from urllib.parse import urlencode
from app.models import Tache

# ============================================
# CHARGEMENT .ENV
# ============================================

load_dotenv()

CLIENT_ID = os.getenv("GRAPH_CLIENT_ID")
TENANT_ID = os.getenv("GRAPH_TENANT_ID")
CLIENT_SECRET = os.getenv("GRAPH_CLIENT_SECRET")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://graph.microsoft.com/.default"]

# ============================================
# FONCTIONS DE SYNCHRONISATION
# ============================================

def get_token():
    """Obtient un token d’accès OAuth2 valide pour Microsoft Graph."""
    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET
    )
    result = app.acquire_token_for_client(scopes=SCOPE)
    return result.get("access_token")

def fetch_outlook_events(access_token):
    """Récupère les événements Outlook dans les 30 jours à venir."""
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    today = datetime.utcnow().isoformat()
    future = (datetime.utcnow() + timedelta(days=30)).isoformat()
    url = f"https://graph.microsoft.com/v1.0/me/calendarview?startdatetime={today}&enddatetime={future}"
    response = requests.get(url, headers=headers)
    return response.json().get("value", [])

def sync_to_db(events):
    """Insère les événements dans PlanificationCollaborateur en évitant les doublons."""
    db = SessionLocal()
    try:
        for ev in events:
            sujet = ev.get("subject", "Sans titre")
            date_debut = ev.get("start", {}).get("dateTime", "")
            date_fin = ev.get("end", {}).get("dateTime", "")
            if not date_debut or not date_fin:
                continue
            date_debut = date_debut[:19]
            date_fin = date_fin[:19]
            exists = db.execute(text("""
                SELECT 1 FROM PlanificationCollaborateur
                WHERE sujet = :s AND date_debut = :d1 AND date_fin = :d2
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
    """Lance la synchronisation complète depuis Outlook vers la base."""
    try:
        token = get_token()
        events = fetch_outlook_events(token)
        sync_to_db(events)
        print(f"✔ Outlook sync terminé : {len(events)} événements analysés.")
    except Exception as e:
        print(f"❌ Outlook sync échouée: {e}")

def synchronize_outlook():
    """
    Point d’entrée principal appelé au démarrage du backend.

    Cette fonction déclenche la récupération des événements Outlook
    et l’insertion dans la base, si nécessaire.

    Version:
    --------
    specification: Esteban Barracho (v.2 11/07/2025)
    implement: Esteban Barracho (v.2 11/07/2025)
    """
    from os import getenv
    if not all([getenv("GRAPH_CLIENT_ID"), getenv("GRAPH_TENANT_ID"), getenv("GRAPH_CLIENT_SECRET")]):
        print("⚠️  Identifiants Outlook manquants, synchronisation ignorée.")
        return
    print("🔄 Synchronisation Outlook en cours...")
    launch_sync()


REDIRECT_URI = "http://localhost:8000/outlook/callback"
OAUTH_SCOPE = ["Calendars.ReadWrite"]

def get_oauth_url():
    """Construit l’URL de connexion OAuth pour Microsoft Graph."""
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "response_mode": "query",
        "scope": " ".join(OAUTH_SCOPE),
    }
    return f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize?{urlencode(params)}"

def exchange_code_for_token(code: str):
    """Échange le code d’autorisation contre un token d’accès."""
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
    return res.json().get("access_token")

def create_events_from_db(db, token: str):
    """Ajoute dans Outlook les tâches importantes présentes dans la base."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    taches = db.query(Tache).filter(Tache.est_realisable == 1).limit(5).all()
    count = 0
    for t in taches:
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
