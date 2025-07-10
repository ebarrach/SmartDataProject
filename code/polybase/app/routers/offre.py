# ============================================
# IMPORTS
# ============================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Offre
from app.schemas import OffreCreate, OffreOut
from typing import List

# ============================================
# ROUTER INITIALIZATION
# ============================================

router = APIRouter(
    prefix="/offres",
    tags=["offres"]
)

# ============================================
# CREATE OFFRE
# ============================================

@router.post("/", response_model=OffreOut)
def create_offre(offre: OffreCreate, db: Session = Depends(get_db)):
    """
    Create a new Offre entry.
    Version:
    --------
    specification: Esteban Barracho (v.1 24/06/2025)
    implement: Esteban Barracho (v.1 24/06/2025)
    """
    db_offre = db.query(Offre).filter_by(id_offre=offre.id_offre).first()
    if db_offre:
        raise HTTPException(status_code=400, detail="Offre already exists.")
    new_offre = Offre(**offre.dict())
    db.add(new_offre)
    db.commit()
    db.refresh(new_offre)
    return new_offre

# ============================================
# GET ALL OFFRES
# ============================================

@router.get("/", response_model=List[OffreOut])
def get_offres(db: Session = Depends(get_db)):
    """
    Retrieve all Offres.
    Version:
    --------
    specification: Esteban Barracho (v.1 24/06/2025)
    implement: Esteban Barracho (v.1 24/06/2025)
    """
    return db.query(Offre).all()

# ============================================
# GET OFFRE BY ID
# ============================================

@router.get("/{id_offre}", response_model=OffreOut)
def get_offre(id_offre: str, db: Session = Depends(get_db)):
    """
    Retrieve an Offre by its ID.
    Version:
    --------
    specification: Esteban Barracho (v.1 24/06/2025)
    implement: Esteban Barracho (v.1 24/06/2025)
    """
    offre = db.query(Offre).filter_by(id_offre=id_offre).first()
    if not offre:
        raise HTTPException(status_code=404, detail="Offre not found.")
    return offre

# ============================================
# DELETE OFFRE
# ============================================

@router.delete("/{id_offre}")
def delete_offre(id_offre: str, db: Session = Depends(get_db)):
    """
    Delete an Offre by its ID.
    Version:
    --------
    specification: Esteban Barracho (v.1 24/06/2025)
    implement: Esteban Barracho (v.1 24/06/2025)
    """
    offre = db.query(Offre).filter_by(id_offre=id_offre).first()
    if not offre:
        raise HTTPException(status_code=404, detail="Offre not found.")
    db.delete(offre)
    db.commit()
    return {"detail": "Offre deleted successfully."}
