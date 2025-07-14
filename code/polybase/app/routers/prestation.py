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
    Raises 404 if not found.
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
    """Creates and stores a new prestation entry.
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
    """Updates an existing prestation with new values.
    Raises 404 if not found.
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
    """Deletes a prestation entry from the database.
    Raises 404 if not found.
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
    """Deletes a facture entry from the database.
    Raises 404 if not found.
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

@router.post("/api/encodage")
def encodage_libre(
    date: date = Form(...),
    id_projet: str = Form(...),
    heures_effectuees: float = Form(...),
    commentaire: str = Form(...),
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
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
