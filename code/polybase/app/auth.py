from fastapi import Depends, HTTPException, Cookie
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Personnel

# Simulation d'une authentification par cookie

def get_current_user(session_id: str = Cookie(None), db: Session = Depends(SessionLocal)):
    user = db.query(Personnel).filter(Personnel.id_personnel == session_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
    return user