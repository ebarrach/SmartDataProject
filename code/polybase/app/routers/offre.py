# ============================================
# IMPORTS
# ============================================

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Offre
from app.schemas import OffreCreate, OffreOut

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
    """Create a new Offre entry.
    Parameters:
    -----------
    offre : OffreCreate
        Pydantic schema containing data for the new offer.
    db : Session
        Active SQLAlchemy session used to interact with the database.
    Returns:
    --------
    Offre
        The newly created offer record.
    Raises:
    -------
    HTTPException (400)
        If an offer with the same ID already exists.
    AssertionError
        If the created object is not of type Offre.
    Version:
    --------
    specification: Esteban Barracho (v.1 24/06/2025)
    implement: Esteban Barracho (v.1 24/06/2025)
    """
    db_offre = db.query(Offre).filter_by(id_offre=offre.id_offre).first()
    if db_offre:
        raise HTTPException(status_code=400, detail="Offre already exists.")
    new_offre = Offre(**offre.dict())
    assert isinstance(new_offre, Offre), "Objet créé invalide (Offre attendu)"
    db.add(new_offre)
    db.commit()
    db.refresh(new_offre)
    return new_offre

# ============================================
# GET ALL OFFRES
# ============================================
@router.get("/", response_model=List[OffreOut])
def get_offres(db: Session = Depends(get_db)):
    """Retrieve all Offres.
    Parameters:
    -----------
    db : Session
        Active SQLAlchemy session used to fetch data from the database.
    Returns:
    --------
    List[OffreOut]
        A list of all offers registered in the database.
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
    """Retrieve an Offre by its ID.
    Parameters:
    -----------
    id_offre : str
        Unique identifier of the offer to retrieve.
    db : Session
        Active SQLAlchemy session used to query the database.
    Returns:
    --------
    OffreOut
        The offer corresponding to the provided ID.
    Raises:
    -------
    HTTPException
        404 if the offer is not found in the database.
    Version:
    --------
    specification: Esteban Barracho (v.1 24/06/2025)
    implement: Esteban Barracho (v.1 24/06/2025)
    """
    assert isinstance(id_offre, str), "L’identifiant de l’offre doit être une chaîne"
    offre = db.query(Offre).filter_by(id_offre=id_offre).first()
    if not offre:
        raise HTTPException(status_code=404, detail="Offre not found.")
    return offre

# ============================================
# DELETE OFFRE
# ============================================
@router.delete("/{id_offre}")
def delete_offre(id_offre: str, db: Session = Depends(get_db)):
    """Delete an Offre by its ID.
    Parameters:
    -----------
    id_offre : str
        Unique identifier of the offer to delete.
    db : Session
        Active SQLAlchemy session used to perform deletion.
    Returns:
    --------
    dict
        Confirmation message indicating successful deletion.
    Raises:
    -------
    HTTPException
        404 if the offer is not found in the database.
    Version:
    --------
    specification: Esteban Barracho (v.1 24/06/2025)
    implement: Esteban Barracho (v.1 24/06/2025)
    """
    assert isinstance(id_offre, str), "L’identifiant de l’offre doit être une chaîne"
    offre = db.query(Offre).filter_by(id_offre=id_offre).first()
    if not offre:
        raise HTTPException(status_code=404, detail="Offre not found.")
    db.delete(offre)
    db.commit()
    return {"detail": "Offre deleted successfully."}
