from fastapi import FastAPI
from app.routers import user, analytics

app = FastAPI()

app.include_router(user.router)
app.include_router(analytics.router)

@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API PolyBase"}