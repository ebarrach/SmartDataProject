# ============================================
# IMPORTS
# ============================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Projet, Phase, Facture
from app.schemas import ProjetCreate, ProjetOut, PhaseCreate, PhaseOut

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
# ROUTE : List all projects
# ============================================

@router.get("/projects", response_model=list[ProjetOut])
def list_projects(db: Session = Depends(get_db)):
    """Returns all projects registered in the system.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
    return db.query(Projet).all()

# ============================================
# ROUTE : Get a specific project
# ============================================

@router.get("/projects/{id_projet}", response_model=ProjetOut)
def get_project(id_projet: str, db: Session = Depends(get_db)):
    """Returns a project by its ID.
    Raises 404 if not found.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
    project = db.query(Projet).filter(Projet.id_projet == id_projet).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

# ============================================
# ROUTE : Create a new project
# ============================================

@router.post("/projects", response_model=ProjetOut)
def create_project(project: ProjetCreate, db: Session = Depends(get_db)):
    """Creates and stores a new project.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
    db_project = Projet(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

# ============================================
# ROUTE : List phases of a project
# ============================================

@router.get("/projects/{id_projet}/phases", response_model=list[PhaseOut])
def list_phases(id_projet: str, db: Session = Depends(get_db)):
    """Returns all phases linked to a project via its invoice reference.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
    return db.query(Phase).filter(Phase.id_facture == id_projet).all()

# ============================================
# ROUTE : Add a phase to a project
# ============================================

@router.post("/projects/{id_projet}/phases", response_model=PhaseOut)
def add_phase(id_projet: str, phase: PhaseCreate, db: Session = Depends(get_db)):
    """Adds a new phase to a given project.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
    new_phase = Phase(**phase.dict())
    db.add(new_phase)
    db.commit()
    db.refresh(new_phase)
    return new_phase

# ============================================
# ROUTE : Delete a project
# ============================================

@router.delete("/projects/{id_projet}")
def delete_project(id_projet: str, db: Session = Depends(get_db)):
    """Deletes a project from the database.
    Raises 404 if not found.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 21/06/2025)
    """
    project = db.query(Projet).filter(Projet.id_projet == id_projet).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"message": f"Project {id_projet} deleted successfully"}

# ============================================
# ROUTE : Delete a phase
# ============================================

@router.delete("/phases/{id_phase}")
def delete_phase(id_phase: str, db: Session = Depends(get_db)):
    """Deletes a phase from the database.
    Raises 404 if not found.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 21/06/2025)
    """
    phase = db.query(Phase).filter(Phase.id_phase == id_phase).first()
    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")
    db.delete(phase)
    db.commit()
    return {"message": f"Phase {id_phase} deleted successfully"}

# ============================================
# ROUTE : Delete a facture
# ============================================

@router.delete("/factures/{id_facture}")
def delete_facture(id_facture: str, db: Session = Depends(get_db)):
    """Deletes a facture from the database.
    Raises 404 if not found.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 21/06/2025)
    """
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
