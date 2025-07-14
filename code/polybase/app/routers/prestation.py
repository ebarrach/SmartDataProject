# ============================================
# IMPORTS
# ============================================

from fastapi import APIRouter, Depends, HTTPException
from fastapi import Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import date
from app.auth import get_current_user

from app.database import SessionLocal
from app.models import PrestationCollaborateur, Facture
from app.schemas import PrestationCreate, PrestationOut
from app.models import PrestationCollaborateur
from app.routers.admin import generate_id

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
# ROUTE : List all prestations
# ============================================
@router.get("/prestation", response_model=list[PrestationOut])
def list_prestations(db: Session = Depends(get_db)):
    """Returns all prestation records from the database.
    Parameters:
    -----------
    db : Session
        Active SQLAlchemy session used to query the prestations table.
    Returns:
    --------
    list[PrestationOut]
        List of all PrestationCollaborateur entries stored in the system.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
    return db.query(PrestationCollaborateur).all()

# ============================================
# ROUTE : Get one prestation by ID
# ============================================
@router.get("/prestation/{id_prestation}", response_model=PrestationOut)
def get_prestation(id_prestation: str, db: Session = Depends(get_db)):
    """Returns a specific prestation based on its ID.
    Raises 404 if the prestation does not exist.
    Parameters:
    -----------
    id_prestation : str
        Unique identifier of the prestation to retrieve.
    db : Session
        Active SQLAlchemy session used for the database query.
    Returns:
    --------
    PrestationOut
        Prestation object matching the given ID.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.2 22/06/2025)
    """
    assert isinstance(id_prestation, str), "L’identifiant de prestation doit être une chaîne"
    prestation = db.query(PrestationCollaborateur).filter_by(id_prestation=id_prestation).first()
    if not prestation:
        raise HTTPException(status_code=404, detail="Prestation not found")
    return prestation

# ============================================
# ROUTE : Create a new prestation
# ============================================
@router.post("/prestation", response_model=PrestationOut)
def create_prestation(prestation: PrestationCreate, db: Session = Depends(get_db)):
    """Creates and stores a new prestation entry in the database.
    Parameters:
    -----------
    prestation : PrestationCreate
        Pydantic model containing the data for the new prestation.
    db : Session
        Active SQLAlchemy session used to persist the prestation.
    Returns:
    --------
    PrestationOut
        The newly created prestation object after database insertion.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
    db_prestation = PrestationCollaborateur(**prestation.dict())
    assert isinstance(db_prestation, PrestationCollaborateur), "Objet créé invalide (PrestationCollaborateur attendu)"
    db.add(db_prestation)
    db.commit()
    db.refresh(db_prestation)
    return db_prestation

# ============================================
# ROUTE : Update an existing prestation
# ============================================
@router.put("/prestation/{id_prestation}", response_model=PrestationOut)
def update_prestation(id_prestation: str, updated: PrestationCreate, db: Session = Depends(get_db)):
    """Updates an existing prestation with new values based on the provided ID.
    Parameters:
    -----------
    id_prestation : str
        Identifier of the prestation to update.
    updated : PrestationCreate
        Updated data for the prestation.
    db : Session
        Active SQLAlchemy session used to perform the update.
    Returns:
    --------
    PrestationOut
        The updated prestation object after modification.
    Raises:
    -------
    HTTPException (404)
        If no prestation is found with the given ID.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.2 22/06/2025)
    """
    prestation = db.query(PrestationCollaborateur).filter_by(id_prestation=id_prestation).first()
    if not prestation:
        raise HTTPException(status_code=404, detail="Prestation not found")
    for key, value in updated.dict().items():
        assert hasattr(prestation, key), f"Champ '{key}' introuvable dans PrestationCollaborateur"
        setattr(prestation, key, value)
    db.commit()
    db.refresh(prestation)
    return prestation

# ============================================
# ROUTE : Delete a prestation
# ============================================
@router.delete("/prestation/{id_prestation}")
def delete_prestation(id_prestation: str, db: Session = Depends(get_db)):
    """Deletes a prestation entry from the database using its ID.
    Parameters:
    -----------
    id_prestation : str
        Identifier of the prestation to delete.
    db : Session
        Active SQLAlchemy session used for database interaction.
    Returns:
    --------
    dict
        Confirmation message upon successful deletion.
    Raises:
    -------
    HTTPException (404)
        If no prestation is found with the given ID.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.2 22/06/2025)
    """
    assert isinstance(id_prestation, str), "L’identifiant de prestation doit être une chaîne"
    prestation = db.query(PrestationCollaborateur).filter_by(id_prestation=id_prestation).first()
    if not prestation:
        raise HTTPException(status_code=404, detail="Prestation not found")
    db.delete(prestation)
    db.commit()
    return {"message": "Prestation successfully deleted"}

# ============================================
# ROUTE : Delete a facture
# ============================================
@router.delete("/factures/{id_facture}")
def delete_facture(id_facture: str, db: Session = Depends(get_db)):
    """Deletes a facture entry from the database using its ID.
    Parameters:
    -----------
    id_facture : str
        Identifier of the facture to delete.
    db : Session
        Active SQLAlchemy session used for database interaction.
    Returns:
    --------
    dict
        Confirmation message upon successful deletion.
    Raises:
    -------
    HTTPException (404)
        If no facture is found with the given ID.
    HTTPException (500)
        If an error occurs during deletion (e.g. integrity constraint).
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.2 22/06/2025)
    """
    assert isinstance(id_facture, str), "L’identifiant de facture doit être une chaîne"
    facture = db.query(Facture).filter_by(id_facture=id_facture).first()
    if not facture:
        raise HTTPException(status_code=404, detail="Facture not found")
    try:
        db.delete(facture)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")
    return {"message": f"Facture {id_facture} deleted successfully"}

# ============================================
# MANUAL ENCODING OF A SERVICE
# ============================================
@router.post("/api/encodage")
def encodage_libre(date: date = Form(...),id_projet: str = Form(...),heures_effectuees: float = Form(...),commentaire: str = Form(...), user=Depends(get_current_user), db: Session = Depends(get_db)):
    """This route allows an authenticated user to manually enter
    a service (without linking it to a task), specifying
    the date, project, number of hours worked
    and a comment.
    Parameters:
    -----------
    date: date
        Date on which the service was provided.
    id_projet: str
        Identifier of the project concerned.
    heures_effectuees: float
        Number of hours worked.
    commentaire: str
        Description of the work carried out.
    user: User
        Logged-in user (injected via Depends).
    db: Session
        Injected SQLAlchemy session.
    Return:
    --- ----
    RedirectResponse
        Redirects to the calendar page after successful insertion.
    Version:
    --------
    specification: Esteban Barracho (v.1 14/07/2025)
    implement: Esteban Barracho (v.1 14/07/2025)
    """
    new_id = generate_id("PC")
    prestation = PrestationCollaborateur(
        id_prestation=new_id,
        date=date,
        id_tache=None,
        id_projet=id_projet,
        id_collaborateur=user.id_personnel,
        heures_effectuees=heures_effectuees,
        mode_facturation="horaire",
        facture_associee=None,
        taux_horaire=user.taux_honoraire_standard,
        commentaire=commentaire
    )
    db.add(prestation)
    db.commit()
    return RedirectResponse(url="/agenda", status_code=302)
