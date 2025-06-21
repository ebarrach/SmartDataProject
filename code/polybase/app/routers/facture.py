from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Facture
from ..schemas import FactureOut
from ..schemas import BaseModel, date
from typing import Optional

class FactureCreate(BaseModel):
    id_facture: str
    date_emission: date
    montant_facture: float
    transmission_electronique: bool
    annexe: str
    statut: str
    reference_banque: str
    fichier_facture: str

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/factures", response_model=list[FactureOut])
def list_factures(db: Session = Depends(get_db)):
    return db.query(Facture).all()

@router.get("/factures/{id_facture}", response_model=FactureOut)
def get_facture(id_facture: str, db: Session = Depends(get_db)):
    facture = db.query(Facture).filter(Facture.id_facture == id_facture).first()
    if not facture:
        raise HTTPException(status_code=404, detail="Facture non trouvée")
    return facture

@router.post("/factures", response_model=FactureOut)
def create_facture(facture: FactureCreate, db: Session = Depends(get_db)):
    db_facture = Facture(**facture.dict())
    db.add(db_facture)
    db.commit()
    db.refresh(db_facture)
    return db_facture

@router.put("/factures/{id_facture}", response_model=FactureOut)
def update_facture(id_facture: str, facture_update: FactureCreate, db: Session = Depends(get_db)):
    facture = db.query(Facture).filter(Facture.id_facture == id_facture).first()
    if not facture:
        raise HTTPException(status_code=404, detail="Facture non trouvée")
    for key, value in facture_update.dict().items():
        setattr(facture, key, value)
    db.commit()
    db.refresh(facture)
    return facture

@router.delete("/factures/{id_facture}")
def delete_facture(id_facture: str, db: Session = Depends(get_db)):
    facture = db.query(Facture).filter(Facture.id_facture == id_facture).first()
    if not facture:
        raise HTTPException(status_code=404, detail="Facture non trouvée")
    db.delete(facture)
    db.commit()
    return {"message": "Facture supprimée avec succès"}
