# ============================================
# IMPORTS
# ============================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Collaborateur
from pydantic import BaseModel


# ============================================
# ROUTER INITIALIZATION
# ============================================

router = APIRouter()

# ============================================
# UTILITY : Database session
# ============================================

def get_db():
    """Provides a database session for dependency injection.
    Yields:
    -------
    Session: SQLAlchemy session instance.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
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
    """Creates a new collaborator entry in the database if it does not already exist.

    Parameters:
    -----------
    collaborateur (CollaborateurIn): Input schema containing the personnel ID.
    db (Session): SQLAlchemy session dependency.

    Returns:
    --------
    dict: Success message indicating creation or existence.

    Version:
    --------
    specification: Esteban Barracho (v.1 21/06/2025)
    implement: Esteban Barracho (v.1.2 22/06/2025)
    """
    existing = db.query(Collaborateur).filter(Collaborateur.id_personnel == collaborateur.id_personnel).first()
    if existing:
        return {"message": "Collaborateur already exists"}
    nouveau = Collaborateur(id_personnel=collaborateur.id_personnel)
    db.add(nouveau)
    db.commit()
    return {"message": f"Collaborateur {collaborateur.id_personnel} created"}

