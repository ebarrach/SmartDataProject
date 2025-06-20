from fastapi import FastAPI
from app.routers import user, analytics
import os

app = FastAPI()

app.include_router(user.router)
app.include_router(analytics.router)

@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API PolyBase"}

@app.on_event("startup")
def startup_message():
    print(f"✅ API disponible sur http://localhost:{os.getenv('PORT', 8000)}")