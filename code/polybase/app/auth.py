from fastapi import Depends, HTTPException, Cookie, Request
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Personnel

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Simulation d'une authentification simple (à adapter avec mot de passe hashé si besoin)
def authenticate_user(email: str, db: Session):
    user = db.query(Personnel).filter(Personnel.email == email).first()
    return user

# Récupère l'utilisateur via cookie
def get_current_user(session_id: str = Cookie(None), db: Session = Depends(get_db)):
    if not session_id:
        raise HTTPException(status_code=401, detail="Session non trouvée")
    user = db.query(Personnel).filter(Personnel.id_personnel == session_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
    return user
