# ============================================
# MODULE : Collaborateur
# ============================================
# specification: Esteban Barracho (v.1 21/06/2025)
# implement: Esteban Barracho (v.2 22/06/2025)
# ============================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Collaborateur
from pydantic import BaseModel

router = APIRouter()

# ============================================
# UTILITY : Database session
# ============================================

def get_db():
    """Yields a database session using SQLAlchemy."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================
# SCHEMA : Input
# ============================================

class CollaborateurIn(BaseModel):
    id_personnel: str

# ============================================
# ENDPOINT : Create Collaborateur
# ============================================

@router.post("/collaborateurs")
def create_collaborateur(collaborateur: CollaborateurIn, db: Session = Depends(get_db)):
    existing = db.query(Collaborateur).filter(Collaborateur.id_personnel == collaborateur.id_personnel).first()
    if existing:
        return {"message": "Collaborateur already exists"}
    nouveau = Collaborateur(id_personnel=collaborateur.id_personnel)
    db.add(nouveau)
    db.commit()
    return {"message": f"Collaborateur {collaborateur.id_personnel} created"}
