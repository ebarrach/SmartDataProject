# ============================================
# IMPORTS
# ============================================

from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.status import HTTP_302_FOUND
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError

import app.utils.openrouter_adapter as deepseek
import app.utils.outlook_sync as outlook_sync
from app.auth import authenticate_user, get_current_user, get_db
from app.models import Client, Projet
from app.models import Facture, PlanificationCollaborateur, PrestationCollaborateur
from app.routers import admin
from app.routers import collaborateur
from app.routers import finance
from app.routers import offre
from app.routers import outlook
from app.routers import (
    user, analytics, client, project, tache,
    facture, dashboard, planification, prestation
)

# ============================================
# INITIALISATION OF THE FASTAPI APPLICATION
# ============================================

app = FastAPI()
"""This object initializes the FastAPI application.
Version:
--------
specification: Esteban Barracho (v.1 19/06/2025)
implement: Esteban Barracho (v.1 19/06/2025)
"""

# ============================================
# CONFIGURATION OF STATIC FILES & TEMPLATES
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
# MODULE ROUTING
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
app.include_router(admin.router)
app.include_router(outlook.router)
"""These instructions include routers for each domain (user, tache, etc.).
Version:
--------
specification: Esteban Barracho (v.1 19/06/2025)
implement: Esteban Barracho (v.1.3 24/06/2025)
"""

# ============================================
# KICK-OFF EVENT
# ============================================

@app.on_event("startup")
def startup_event():
    """Startup events when the API server is launched.
    Version:
    --------
    specification: Esteban Barracho (v.1 11/07/2025)
    implement: Esteban Barracho (v.2 11/07/2025)
    """
    print("✅ API disponible sur http://localhost:8000")
    try:
        outlook_sync.synchronize_outlook()
    except Exception as e:
        print(f"⚠️  Synchronisation Outlook ignorée : {e}")

    deepseek.prepare_adaptation()

# ============================================
# PUBLIC ROADS (HTML)
# ============================================

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """Displays the login page when accessing the root URL.
    Parameters:
    -----------
    request : Request
        The incoming HTTP request.
    Returns:
    --------
    TemplateResponse
        Renders the login.html template with the request context.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
def login_user(request: Request, email: str = Form(...), password: str = Form(...), code: str = Form(...), db: Session = Depends(get_db)):
    """Processes the information from the user login form with password verification
    and simulation of a 2FA validation code. If authentication is successful, a session is created.
    Parameters:
    -----------
    request: Request
        Incoming HTTP request.
    email: str
        Email address entered by the user.
    password: str
        Password entered by the user.
    code: str
        2FA validation code (simulated here in hard code).
    db: Session
        SQLAlchemy session for user verification.
    Return:
    -------
    HTMLResponse
        Redirect to the dashboard or display the form with an error message.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
    user = authenticate_user(email=email, plain_password=password, db=db)
    if user and code == "123456": #Todo 123456 à changé pour 2AF (idée randint et envoie par mail du code journalié)
        response = RedirectResponse(url="/dashboard", status_code=HTTP_302_FOUND)
        response.set_cookie(key="session_id", value=user.id_personnel)
        return response
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "Email ou code invalide"
    })

@app.get("/logout")
def logout():
    """Logs the user out by clearing the session cookie and redirecting to the login page.
    Returns:
    --------
    RedirectResponse
        Redirects to the root route after removing session data.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
    response = RedirectResponse(url="/")
    response.delete_cookie("session_id")
    return response

# ============================================
# ROUTES PROTECTED BY AUTHENTICATION
# ============================================

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request, user=Depends(get_current_user)):
    """Displays the logged-in user's personalized dashboard, including statistics,
    current tasks, overtime hours, and project indicators. Accessible only after authentication.
    Parameters:
    -----------
    request: Request
        Incoming HTTP request.
    user: User
        Logged-in user, automatically injected via Depends(get_current_user).
    Return:
    -------
    HTMLResponse
        HTML page displaying the user's dashboard.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
    assert user is not None, "Utilisateur non connecté"
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})

@app.get("/agenda", response_class=HTMLResponse)
def agenda_page(request: Request, user=Depends(get_current_user)):
    """Displays the weekly calendar page for the logged-in user, including
    a view of their personal schedule and upcoming tasks. Also allows
    synchronization with Outlook if enabled.
    Parameters:
    -----------
    request: Request
        Incoming HTTP request.
    user: User
        Logged-in user, automatically injected via Depends(get_current_user).
    Return:
    -------
    HTMLResponse
        HTML page of the calendar with mini-calendar, current week, and tasks to be completed.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
    assert user is not None, "Utilisateur non connecté"
    return templates.TemplateResponse("agenda.html", {"request": request, "user": user})

@app.get("/documents", response_class=HTMLResponse)
def documents_page(request: Request, user=Depends(get_current_user)):
    """Displays the page of documents available to the logged-in user,
    including files uploaded or linked to their projects, tasks, or other entities.
    Parameters:
    -----------
    request: Request
        FastAPI object containing the HTTP request information.
    user: User
        Authenticated user, injected via Depends.
    Return:
    -------
    HTMLResponse
        HTML page of documents with injected user context.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
    assert user is not None, "Utilisateur non connecté"
    return templates.TemplateResponse("documents.html", {"request": request, "user": user})

@app.get("/tasks", response_class=HTMLResponse)
def task_list_page(request: Request, user=Depends(get_current_user)):
    """Displays a detailed view of the tasks assigned to the logged-in user.
    Allows you to view descriptions, statuses, and deadlines.
    Parameters:
    -----------
    request: Request
        Incoming HTTP request (FastAPI).
    user: User
        Authenticated user instance (injection via Depends).
    Return:
    -------
    HTMLResponse
        HTML page displaying the user's task details.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
    assert user is not None, "Utilisateur non connecté"
    return templates.TemplateResponse("task_detail.html", {"request": request, "user": user})

@app.get("/clients", response_class=HTMLResponse)
def clients_page(request: Request, user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Displays the customer management page, with the complete list
    of customers in the database.
    Parameters:
    -----------
    request: Request
        Original HTTP request.
    user: User
        Authenticated user (via FastAPI dependency).
    db: Session
        Active SQLAlchemy session for accessing data.
    Return:
    -------
    HTMLResponse
        HTML page containing the list of customers.
    Version:
    --------
    specification: Esteban Barracho (v.1 24/06/2025)
    implement: Esteban Barracho (v.1 24/06/2025)
    """
    assert user is not None, "Utilisateur non connecté"
    clients = db.query(Client).all()
    return templates.TemplateResponse("clients.html", {"request": request, "user": user, "clients": clients})

@app.get("/projects", response_class=HTMLResponse)
def projects_page(request: Request, user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Affiche la page des projets, avec la liste complète
    des projets enregistrés dans la base de données.
    Paramètres:
    -----------
    request : Request
        Objet de requête HTTP transmis automatiquement par FastAPI.
    user : Utilisateur
        Utilisateur authentifié (vérifié via dépendance).
    db : Session
        Session active SQLAlchemy pour effectuer les requêtes.
    Retour:
    -------
    HTMLResponse
        Page HTML affichant tous les projets existants.
    Version:
    --------
    specification: Esteban Barracho (v.1 24/06/2025)
    implement: Esteban Barracho (v.1 24/06/2025)
    """
    assert user is not None, "Utilisateur non connecté"
    projects = db.query(Projet).all()
    return templates.TemplateResponse("projects.html", {"request": request, "user": user, "projects": projects})


@app.get("/factures", response_class=HTMLResponse)
def factures_page(request: Request, user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Displays the invoices page with a full list of issued invoices.
    Parameters:
    -----------
    request : Request
        HTTP request object provided by FastAPI.
    user : User
        Authenticated user object (injected via dependency).
    db : Session
        Active SQLAlchemy session for database operations.
    Returns:
    --------
    HTMLResponse
        Rendered HTML page displaying all invoice records.
    Version:
    --------
    specification: Esteban Barracho (v.1 24/06/2025)
    implement: Esteban Barracho (v.1 24/06/2025)
    """
    assert user is not None, "Utilisateur non connecté"
    factures = db.query(Facture).all()
    return templates.TemplateResponse("factures.html", {"request": request, "user": user, "factures": factures})

@app.get("/planifications", response_class=HTMLResponse)
def planifications_page(request: Request, user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Displays the planning page with a full list of collaborator schedules.
    Parameters:
    -----------
    request : Request
        HTTP request object passed to the template.
    user : User
        Authenticated user required to access the page.
    db : Session
        SQLAlchemy session used to query planification data.
    Returns:
    --------
    HTMLResponse
        Rendered template showing planification details.
    Version:
    --------
    specification: Esteban Barracho (v.1 24/06/2025)
    implement: Esteban Barracho (v.1 24/06/2025)
    """
    assert user is not None, "Utilisateur non connecté"
    planifications = db.query(PlanificationCollaborateur).all()
    return templates.TemplateResponse("planifications.html", {"request": request, "user": user, "planifications": planifications})

@app.get("/prestation", response_class=HTMLResponse)
def prestation_page(request: Request, user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Displays the prestation page with all recorded work entries.
    Parameters:
    -----------
    request : Request
        Incoming HTTP request passed to the template.
    user : User
        Authenticated user accessing the route.
    db : Session
        SQLAlchemy session for querying prestation data.
    Returns:
    --------
    HTMLResponse
        Rendered HTML view with prestation details.
    Version:
    --------
    specification: Esteban Barracho (v.1 24/06/2025)
    implement: Esteban Barracho (v.1 24/06/2025)
    """
    assert user is not None, "Utilisateur non connecté"
    prestations = db.query(PrestationCollaborateur).all()
    return templates.TemplateResponse("prestation.html", {"request": request, "user": user, "prestations": prestations})

@app.get("/finance", response_class=HTMLResponse)
def finance_page(request: Request, user=Depends(get_current_user)):
    """Displays the finance dashboard for authorized users.
    Parameters:
    -----------
    request : Request
        Incoming HTTP request passed to the template.
    user : User
        Authenticated user accessing the route.
    Returns:
    --------
    HTMLResponse
        Rendered HTML finance dashboard page.
    Version:
    --------
    specification: Esteban Barracho (v.1 24/06/2025)
    implement: Esteban Barracho (v.1 24/06/2025)
    """
    assert user is not None, "Utilisateur non connecté"
    return templates.TemplateResponse("finance.html", {"request": request, "user": user})

# ============================================
# GENERIC ERROR HANDLERS
# ============================================

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handles generic HTTP exceptions by returning a user-friendly HTML error page.
    Parameters:
    -----------
    request : Request
        Incoming HTTP request triggering the error.
    exc : StarletteHTTPException
        Raised exception containing status code and details.
    Returns:
    --------
    HTMLResponse
        Rendered custom error page for the client.
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
    """Handles validation errors raised by FastAPI (e.g., missing or malformed form/path data)
    and renders a user-friendly HTML error page.
    Parameters:
    -----------
    request : Request
        The incoming HTTP request that triggered the validation error.
    exc : RequestValidationError
        The validation exception containing error details.
    Returns:
    --------
    TemplateResponse
        A rendered HTML error page with error details and user guidance.
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

@app.get("/encodage", response_class=HTMLResponse)
def encodage_page(request: Request, user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Displays the manual encoding page for a free service, with a dynamic drop-down menu
    of accessible projects. Only logged-in users can access it.
    Parameters:
    -----------
    request: Request
    Current HTTP request (FastAPI).
    user: User
    Authenticated user (inferred via Depends).
    db: Session
    Active SQLAlchemy session for retrieving projects.
    Return:
    -------
    TemplateResponse
        Rendered HTML page containing the encoding form.
    Version:
    --------
    specification: Esteban Barracho (v.1 14/07/2025)
    implement: Esteban Barracho (v.1 14/07/2025)
    """
    assert user is not None, "Utilisateur non connecté"
    projets = db.query(Projet).all()
    return templates.TemplateResponse("encodage.html", {
        "request": request,
        "user": user,
        "projets": projets
    })
