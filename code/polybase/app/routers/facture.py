# ============================================
# IMPORTS
# ============================================

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Facture
from ..schemas import FactureOut

# ============================================
# SCHEMA : CREATE INVOICE
# ============================================
class FactureCreate(BaseModel):
    """Schema for creating a new invoice.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
    id_facture: str
    date_emission: date
    montant_facture: float
    transmission_electronique: bool
    annexe: str
    statut: str
    reference_banque: str
    fichier_facture: str

# ============================================
# ROUTER INITIALIZATION
# ============================================
router = APIRouter()

# ============================================
# DATABASE DEPENDENCY
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
# ROUTE : List all invoices
# ============================================
@router.get("/factures", response_model=list[FactureOut])
def list_factures(db: Session = Depends(get_db)):
    """Returns the full list of invoices stored in the database.
    Parameters:
    -----------
    db : Session
        Active SQLAlchemy session for database access.
    Returns:
    --------
    list[FactureOut]
        List of all invoice entries.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
    return db.query(Facture).all()

# ============================================
# ROUTE : Get one invoice by ID
# ============================================
@router.get("/factures/{id_facture}", response_model=FactureOut)
def get_facture(id_facture: str, db: Session = Depends(get_db)):
    """Returns a specific invoice based on its ID.
    Raises 404 if not found.
    Parameters:
    -----------
    id_facture : str
        Unique identifier of the invoice to retrieve.
    db : Session
        Active SQLAlchemy session for database access.
    Returns:
    --------
    FactureOut
        Invoice object matching the provided ID.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
    assert isinstance(id_facture, str), "L’identifiant de facture doit être une chaîne"
    facture = db.query(Facture).filter(Facture.id_facture == id_facture).first()
    if not facture:
        raise HTTPException(status_code=404, detail="Facture not found")
    return facture

# ============================================
# ROUTE : Create a new invoice
# ============================================
@router.post("/factures", response_model=FactureOut)
def create_facture(facture: FactureCreate, db: Session = Depends(get_db)):
    """Creates and stores a new invoice in the database.
    Parameters:
    -----------
    facture : FactureCreate
        Pydantic model containing invoice data to insert.
    db : Session
        Active SQLAlchemy session for database access.
    Returns:
    --------
    FactureOut
        The created invoice object as stored in the database.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
    db_facture = Facture(**facture.dict())
    assert isinstance(db_facture, Facture), "Objet créé invalide (Facture attendu)"
    db.add(db_facture)
    db.commit()
    db.refresh(db_facture)
    return db_facture

# ============================================
# ROUTE : Update an existing invoice
# ============================================
@router.put("/factures/{id_facture}", response_model=FactureOut)
def update_facture(id_facture: str, facture_update: FactureCreate, db: Session = Depends(get_db)):
    """Updates an existing invoice with new values.
    Parameters:
    -----------
    id_facture : str
        Unique identifier of the invoice to update.
    facture_update : FactureCreate
        Pydantic model containing the updated invoice data.
    db : Session
        Active SQLAlchemy session for database operations.
    Returns:
    --------
    FactureOut
        The updated invoice record from the database.
    Raises:
    -------
    HTTPException
        404 if the invoice does not exist.

    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
    assert isinstance(id_facture, str), "L’identifiant de facture doit être une chaîne"
    facture = db.query(Facture).filter(Facture.id_facture == id_facture).first()
    if not facture:
        raise HTTPException(status_code=404, detail="Facture not found")
    for key, value in facture_update.dict().items():
        assert hasattr(facture, key), f"Champ '{key}' introuvable dans l’objet Facture"
        setattr(facture, key, value)
    db.commit()
    db.refresh(facture)
    return facture

# ============================================
# ROUTE : Delete an invoice
# ============================================
@router.delete("/factures/{id_facture}")
def delete_facture(id_facture: str, db: Session = Depends(get_db)):
    """Deletes an invoice from the database.
    Parameters:
    -----------
    id_facture : str
        Unique identifier of the invoice to delete.
    db : Session
        Active SQLAlchemy session for database operations.
    Returns:
    --------
    dict
        Confirmation message upon successful deletion.
    Raises:
    -------
    HTTPException
        404 if the invoice is not found.
        500 if a database error occurs during deletion.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.2 22/06/2025)
    """
    assert isinstance(id_facture, str), "L’identifiant de facture doit être une chaîne"
    facture = db.query(Facture).filter(Facture.id_facture == id_facture).first()
    if not facture:
        raise HTTPException(status_code=404, detail="Facture not found")
    try:
        db.delete(facture)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")
    return {"message": f"Facture {id_facture} deleted successfully"}
