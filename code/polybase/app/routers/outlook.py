# ============================================
# IMPORTS
# ============================================

import os
import uuid
from datetime import datetime, timedelta
from urllib.parse import urlencode

import requests
from fastapi import APIRouter, Request, Depends, Response, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import PlanificationCollaborateur

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
    """Démarre le processus d’authentification OAuth2 vers Microsoft Outlook.
    Retourne une redirection vers la page d’autorisation de Microsoft avec les bons paramètres
    (client_id, scope, redirect_uri, etc.).

    Returns:
    --------
    RedirectResponse : Redirige l’utilisateur vers la page d’autorisation Microsoft.

    Version:
    --------
    specification: Esteban Barracho (v.1 11/07/2025)
    implement: Esteban Barracho (v.1 11/07/2025)
    """
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
    """Callback de Microsoft pour récupérer un jeton d’accès après autorisation.
    Parameters:
    -----------
    code : str
        Le code temporaire envoyé par Microsoft après validation.
    response : Response
        L’objet de réponse pour définir le cookie de session.

    Returns:
    --------
    RedirectResponse : Redirige vers la page `/agenda` avec le token stocké en cookie.

    Raises:
    -------
    HTTPException : En cas d’erreur durant la récupération du token.

    Version:
    --------
    specification: Esteban Barracho (v.1 11/07/2025)
    implement: Esteban Barracho (v.1 11/07/2025)
    """
    assert isinstance(code, str) and code.strip(), "Code d'autorisation invalide ou manquant"
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
    assert isinstance(token, str) and len(token) > 10, "Token OAuth2 invalide"
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
    """Récupère l’ensemble des événements planifiés : locaux et Outlook.
    Parameters:
    -----------
    request : Request
        Objet HTTP contenant les cookies de session (token Outlook).
    db : Session
        Session SQLAlchemy pour accéder à la base locale.

    Returns:
    --------
    JSONResponse : Liste fusionnée des événements locaux et Outlook.

    Version:
    --------
    specification: Esteban Barracho (v.1 11/07/2025)
    implement: Esteban Barracho (v.1 11/07/2025)
    """
    all_events = []

    # Événements locaux
    db_events = db.query(PlanificationCollaborateur).all()
    for ev in db_events:
        assert hasattr(ev, "sujet") and hasattr(ev, "date_debut") and hasattr(ev,
                                                                              "date_fin"), "Événement local mal formé"
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
                assert isinstance(ev, dict), "Format d’événement Outlook inattendu"
                all_events.append({
                    "sujet": ev.get("subject", "Sans titre"),
                    "date_debut": ev.get("start", {}).get("dateTime", ""),
                    "date_fin": ev.get("end", {}).get("dateTime", ""),
                    "source": "outlook"
                })

    return JSONResponse(content=all_events)
