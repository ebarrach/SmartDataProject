# ============================================
# IMPORTS
# ============================================

from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.status import HTTP_302_FOUND
import os

from app.routers import (
    user, analytics, client, project, tache,
    facture, dashboard, planification, prestation
)

from app.auth import authenticate_user, get_current_user, get_db
from app.routers import collaborateur
from app.routers import finance
from app.models import Client, Projet
from app.models import Facture, PlanificationCollaborateur, PrestationCollaborateur
from app.routers import offre
# ============================================
# INITIALISATION DE L'APPLICATION FASTAPI
# ============================================

app = FastAPI()
"""This object initializes the FastAPI application.
Version:
--------
specification: Esteban Barracho (v.1 19/06/2025)
implement: Esteban Barracho (v.1 19/06/2025)
"""

# ============================================
# CONFIGURATION DES FICHIERS STATIQUES & TEMPLATES
# ============================================

app.mount("/static", StaticFiles(directory="static"), name="static")
"""This instruction mounts the static directory under the /static path.
Version:
--------
specification: Esteban Barracho (v.1 19/06/2025)
implement: Esteban Barracho (v.1 19/06/2025)
"""

templates = Jinja2Templates(directory="templates")
"""This object defines the folder path used for HTML Jinja2 templates.
Version:
--------
specification: Esteban Barracho (v.1 19/06/2025)
implement: Esteban Barracho (v.1 19/06/2025)
"""

# ============================================
# ROUTAGE DES MODULES
# ============================================

app.include_router(user.router)
app.include_router(analytics.router)
app.include_router(client.router)
app.include_router(project.router)
app.include_router(tache.router)
app.include_router(facture.router)
app.include_router(dashboard.router)
app.include_router(planification.router)
app.include_router(prestation.router)

app.include_router(collaborateur.router)

app.include_router(finance.router)
app.include_router(offre.router)

"""These instructions include routers for each domain (user, tache, etc.).
Version:
--------
specification: Esteban Barracho (v.1 19/06/2025)
implement: Esteban Barracho (v.1.3 24/06/2025)
"""

# ============================================
# ROUTES PUBLIQUES (HTML)
# ============================================

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """This route returns the login page.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
def login_user(
        request: Request,
        email: str = Form(...),
        password: str = Form(...),
        code: str = Form(...),
        db: Session = Depends(get_db)
):
    """This route processes the login form and simulates 2FA authentication.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    user = authenticate_user(email=email, plain_password=password, db=db)

    if user and code == "123456":
        response = RedirectResponse(url="/dashboard", status_code=HTTP_302_FOUND)
        response.set_cookie(key="session_id", value=user.id_personnel)
        return response

    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "Email ou code invalide"
    })


@app.get("/logout")
def logout():
    """This route handles logout by deleting the session cookie.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    response = RedirectResponse(url="/")
    response.delete_cookie("session_id")
    return response

# ============================================
# ROUTES PROTÉGÉES PAR AUTHENTIFICATION
# ============================================

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request, user=Depends(get_current_user)):
    """This route renders the dashboard view for the authenticated user.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})


@app.get("/agenda", response_class=HTMLResponse)
def agenda_page(request: Request, user=Depends(get_current_user)):
    """This route renders the agenda page with weekly and task views.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    return templates.TemplateResponse("agenda.html", {"request": request, "user": user})


@app.get("/documents", response_class=HTMLResponse)
def documents_page(request: Request, user=Depends(get_current_user)):
    """This route displays uploaded or linked documents.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    return templates.TemplateResponse("documents.html", {"request": request, "user": user})


@app.get("/tasks", response_class=HTMLResponse)
def task_list_page(request: Request, user=Depends(get_current_user)):
    """This route displays the detailed task view for the user.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    return templates.TemplateResponse("task_detail.html", {"request": request, "user": user})


@app.get("/clients", response_class=HTMLResponse)
def clients_page(request: Request, user=Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Renders the clients page with a list of clients.

    Version:
    --------
    specification: Esteban Barracho (v.1 24/06/2025)
    implement: Esteban Barracho (v.1 24/06/2025)
    """
    clients = db.query(Client).all()
    return templates.TemplateResponse("clients.html", {"request": request, "user": user, "clients": clients})

@app.get("/projects", response_class=HTMLResponse)
def projects_page(request: Request, user=Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Renders the projects page with a list of projects.

    Version:
    --------
    specification: Esteban Barracho (v.1 24/06/2025)
    implement: Esteban Barracho (v.1 24/06/2025)
    """
    projects = db.query(Projet).all()
    return templates.TemplateResponse("projects.html", {"request": request, "user": user, "projects": projects})

@app.get("/factures", response_class=HTMLResponse)
def factures_page(request: Request, user=Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Renders the factures page with a list of invoices.

    Version:
    --------
    specification: Esteban Barracho (v.1 24/06/2025)
    implement: Esteban Barracho (v.1 24/06/2025)
    """
    factures = db.query(Facture).all()
    return templates.TemplateResponse("factures.html", {"request": request, "user": user, "factures": factures})

@app.get("/planifications", response_class=HTMLResponse)
def planifications_page(request: Request, user=Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Renders the planifications page with a list of planifications.

    Version:
    --------
    specification: Esteban Barracho (v.1 24/06/2025)
    implement: Esteban Barracho (v.1 24/06/2025)
    """
    planifications = db.query(PlanificationCollaborateur).all()
    return templates.TemplateResponse("planifications.html", {"request": request, "user": user, "planifications": planifications})

@app.get("/prestation", response_class=HTMLResponse)
def prestation_page(request: Request, user=Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Renders the prestations page with a list of prestations.

    Version:
    --------
    specification: Esteban Barracho (v.1 24/06/2025)
    implement: Esteban Barracho (v.1 24/06/2025)
    """
    prestations = db.query(PrestationCollaborateur).all()
    return templates.TemplateResponse("prestation.html", {"request": request, "user": user, "prestations": prestations})

@app.get("/finance", response_class=HTMLResponse)
def finance_page(request: Request, user=Depends(get_current_user)):
    """
    Renders the finance dashboard page.

    Version:
    --------
    specification: Esteban Barracho (v.1 24/06/2025)
    implement: Esteban Barracho (v.1 24/06/2025)
    """
    return templates.TemplateResponse("finance.html", {"request": request, "user": user})
# ============================================
# ÉVÉNEMENT DE DÉMARRAGE
# ============================================

@app.on_event("startup")
def startup_message():
    """This event is triggered when the API server starts.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    print("✅ API disponible sur http://localhost:8000")


# ============================================
# HANDLERS D’ERREURS GÉNÉRIQUES
# ============================================

from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    """This handler renders a custom HTML error page for HTTP exceptions.
    Version:
    --------
    specification: Esteban Barracho (v.1 23/06/2025)
    implement: Esteban Barracho (v.1 23/06/2025)
    """
    return templates.TemplateResponse("error.html", {
        "request": request,
        "code": exc.status_code,
        "message": exc.detail or "Une erreur est survenue",
        "hint": "Veuillez vérifier l’adresse ou contacter l’administrateur."
    }, status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """This handler renders a custom HTML page for form or path validation errors.
    Version:
    --------
    specification: Esteban Barracho (v.1 23/06/2025)
    implement: Esteban Barracho (v.1 23/06/2025)
    """
    return templates.TemplateResponse("error.html", {
        "request": request,
        "code": 422,
        "message": "Erreur de validation",
        "hint": "Vérifie les champs saisis ou l’URL appelée."
    }, status_code=422)

