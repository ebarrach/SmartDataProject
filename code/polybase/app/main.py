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

app = FastAPI()

# Monter les fichiers statiques
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuration des templates
templates = Jinja2Templates(directory="templates")

# Inclusion des API REST
app.include_router(user.router)
app.include_router(analytics.router)
app.include_router(client.router)
app.include_router(project.router)
app.include_router(tache.router)
app.include_router(facture.router)
app.include_router(dashboard.router)
app.include_router(planification.router)
app.include_router(prestation.router)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
def login_user(
        request: Request,
        email: str = Form(...),
        password: str = Form(...),  # simulé
        code: str = Form(...),
        db: Session = Depends(get_db)
):
    user = authenticate_user(email=email, db=db)

    if user and code == "123456":  # simple 2FA simulé
        response = RedirectResponse(url="/dashboard", status_code=HTTP_302_FOUND)
        response.set_cookie(key="session_id", value=user.id_personnel)
        return response

    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "Email ou code invalide"
    })

@app.get("/logout")
def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("session_id")
    return response

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})

@app.get("/agenda", response_class=HTMLResponse)
def agenda_page(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("agenda.html", {"request": request, "user": user})

@app.get("/documents", response_class=HTMLResponse)
def documents_page(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("documents.html", {"request": request, "user": user})

@app.get("/tasks", response_class=HTMLResponse)
def task_list_page(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("task_detail.html", {"request": request, "user": user})

@app.on_event("startup")
def startup_message():
    print("✅ API disponible sur http://localhost:8000")
