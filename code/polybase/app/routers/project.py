# ============================================
# IMPORTS
# ============================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Projet, Phase
from ..schemas import ProjetCreate, ProjetOut, PhaseCreate, PhaseOut

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
