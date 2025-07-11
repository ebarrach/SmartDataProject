# ============================================
# ROUTEUR OUTLOOK AVEC CONNEXION UTILISATEUR
# specification: Esteban Barracho (v.2 11/07/2025)
# implement: Esteban Barracho (v.2 11/07/2025)
# ============================================

from fastapi import APIRouter, Request, Depends, Response, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse, JSONResponse
from app.database import get_db
from app.models import PlanificationCollaborateur
from datetime import datetime, timedelta
import os
import requests
from urllib.parse import urlencode
import uuid

router = APIRouter()

# --------------------------------------------
# Configuration dynamique OAuth2
# --------------------------------------------
CLIENT_ID = os.getenv("GRAPH_CLIENT_ID")
CLIENT_SECRET = os.getenv("GRAPH_CLIENT_SECRET")
TENANT_ID = os.getenv("GRAPH_TENANT_ID")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
REDIRECT_URI = "http://localhost:8000/outlook/callback"
SCOPE = ["Calendars.Read"]
SESSION_KEY = "outlook_token"

# --------------------------------------------
# Étape 1: Lancer l'autorisation Microsoft
# --------------------------------------------
@router.get("/outlook/login")
def outlook_login():
    state = str(uuid.uuid4())
    query = urlencode({
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "response_mode": "query",
        "scope": " ".join(SCOPE),
        "state": state
    })
    return RedirectResponse(url=f"{AUTHORITY}/oauth2/v2.0/authorize?{query}")

# --------------------------------------------
# Étape 2: Récupération du token via callback
# --------------------------------------------
@router.get("/outlook/callback")
def outlook_callback(code: str, response: Response):
    data = {
        "client_id": CLIENT_ID,
        "scope": " ".join(SCOPE),
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
        "client_secret": CLIENT_SECRET
    }
    r = requests.post(f"{AUTHORITY}/oauth2/v2.0/token", data=data)
    if r.status_code != 200:
        raise HTTPException(status_code=400, detail="Erreur OAuth2")

    token = r.json().get("access_token")
    if not token:
        raise HTTPException(status_code=400, detail="Token manquant")

    response = RedirectResponse(url="/agenda")
    response.set_cookie(key=SESSION_KEY, value=token, httponly=True, max_age=3600)
    return response

# --------------------------------------------
# Route API: Récupérer les événements Outlook + locaux
# --------------------------------------------
@router.get("/outlook/events")
def get_all_events(request: Request, db: Session = Depends(get_db)):
    all_events = []

    # Événements locaux
    db_events = db.query(PlanificationCollaborateur).all()
    for ev in db_events:
        all_events.append({
            "sujet": ev.sujet,
            "date_debut": ev.date_debut.isoformat(),
            "date_fin": ev.date_fin.isoformat(),
            "source": ev.source or "local"
        })

    # Événements Outlook si connecté
    token = request.cookies.get(SESSION_KEY)
    if token:
        today = datetime.utcnow().isoformat()
        future = (datetime.utcnow() + timedelta(days=30)).isoformat()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"https://graph.microsoft.com/v1.0/me/calendarview?startdatetime={today}&enddatetime={future}"
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            for ev in res.json().get("value", []):
                all_events.append({
                    "sujet": ev.get("subject", "Sans titre"),
                    "date_debut": ev.get("start", {}).get("dateTime", ""),
                    "date_fin": ev.get("end", {}).get("dateTime", ""),
                    "source": "outlook"
                })

    return JSONResponse(content=all_events)
