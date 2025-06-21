from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Collaborateur
from pydantic import BaseModel

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class CollaborateurIn(BaseModel):
    id_personnel: str

@router.post("/collaborateurs")
def create_collaborateur(collaborateur: CollaborateurIn, db: Session = Depends(get_db)):
    existing = db.query(Collaborateur).filter(Collaborateur.id_personnel == collaborateur.id_personnel).first()
    if existing:
        return {"message": "Collaborateur already exists"}
    nouveau = Collaborateur(id_personnel=collaborateur.id_personnel)
    db.add(nouveau)
    db.commit()
    return {"message": f"Collaborateur {collaborateur.id_personnel} created"}
