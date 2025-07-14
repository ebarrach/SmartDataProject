# ============================================
# IMPORTS
# ============================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import PlanificationCollaborateur, Facture
from app.schemas import PlanificationCreate, PlanificationOut

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
# ROUTE : List all planifications
# ============================================
@router.get("/planifications", response_model=list[PlanificationOut])
def list_planifications(db: Session = Depends(get_db)):
    """Returns all collaborator task planifications.
    Parameters:
    -----------
    db : Session
        Active SQLAlchemy session used for database interaction.
    Returns:
    --------
    list[PlanificationOut]
        List of all task planification records.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
    return db.query(PlanificationCollaborateur).all()

# ============================================
# ROUTE : Get one planification by ID
# ============================================
@router.get("/planifications/{id_planification}", response_model=PlanificationOut)
def get_planification(id_planification: str, db: Session = Depends(get_db)):
    """Returns a specific planification by ID.
    Raises 404 if not found.
    Parameters:
    -----------
    id_planification : str
        Unique identifier of the planification.
    db : Session
        Active SQLAlchemy session used for database interaction.
    Returns:
    --------
    PlanificationOut
        The planification object matching the provided ID.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
    assert isinstance(id_planification, str), "L’identifiant de planification doit être une chaîne"
    plan = db.query(PlanificationCollaborateur).filter(
        PlanificationCollaborateur.id_planification == id_planification
    ).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Planification not found")
    return plan

# ============================================
# ROUTE : Create a new planification
# ============================================
@router.post("/planifications", response_model=PlanificationOut)
def create_planification(plan: PlanificationCreate, db: Session = Depends(get_db)):
    """
    Creates and stores a new planification entry.

    Parameters:
    -----------
    plan : PlanificationCreate
        The planification data to insert into the database.
    db : Session
        Active SQLAlchemy session used for database interaction.

    Returns:
    --------
    PlanificationOut
        The newly created planification object.

    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
    db_plan = PlanificationCollaborateur(**plan.dict())
    assert isinstance(db_plan, PlanificationCollaborateur), "Objet créé invalide (PlanificationCollaborateur attendu)"
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

# ============================================
# ROUTE : Update an existing planification
# ============================================
@router.put("/planifications/{id_planification}", response_model=PlanificationOut)
def update_planification(id_planification: str, plan_update: PlanificationCreate, db: Session = Depends(get_db)):
    """Updates an existing planification entry.
    Parameters:
    -----------
    id_planification : str
        The unique identifier of the planification to update.
    plan_update : PlanificationCreate
        The new values to apply to the planification.
    db : Session
        Active SQLAlchemy session used for database operations.
    Returns:
    --------
    PlanificationOut
        The updated planification object.
    Raises:
    -------
    HTTPException (404)
        If the planification does not exist.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
    plan = db.query(PlanificationCollaborateur).filter(
        PlanificationCollaborateur.id_planification == id_planification
    ).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Planification not found")
    for key, value in plan_update.dict().items():
        assert hasattr(plan, key), f"Champ '{key}' introuvable dans PlanificationCollaborateur"
        setattr(plan, key, value)
    db.commit()
    db.refresh(plan)
    return plan

# ============================================
# ROUTE : Delete a planification
# ============================================
@router.delete("/planifications/{id_planification}")
def delete_planification(id_planification: str, db: Session = Depends(get_db)):
    """Deletes a planification from the database.
    Parameters:
    -----------
    id_planification : str
        The unique identifier of the planification to delete.
    db : Session
        Active SQLAlchemy session used for database operations.
    Returns:
    --------
    dict
        A confirmation message upon successful deletion.
    Raises:
    -------
    HTTPException (404)
        If the planification does not exist.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
    assert isinstance(id_planification, str), "L’identifiant de planification doit être une chaîne"
    plan = db.query(PlanificationCollaborateur).filter(
        PlanificationCollaborateur.id_planification == id_planification
    ).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Planification not found")
    db.delete(plan)
    db.commit()
    return {"message": "Planification successfully deleted"}

# ============================================
# ROUTE : Delete a facture (temporary fix included here)
# ============================================
@router.delete("/factures/{id_facture}")
def delete_facture(id_facture: str, db: Session = Depends(get_db)):
    """Deletes a facture from the database.
    Parameters:
    -----------
    id_facture : str
        The unique identifier of the invoice to delete.
    db : Session
        Active SQLAlchemy session used for database operations.
    Returns:
    --------
    dict
        A confirmation message upon successful deletion.
    Raises:
    -------
    HTTPException (404)
        If the facture does not exist.
    HTTPException (500)
        If an error occurs during deletion.
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

