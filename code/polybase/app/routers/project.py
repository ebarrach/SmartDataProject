from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Projet, Phase
from ..schemas import ProjetCreate, ProjetOut, PhaseCreate, PhaseOut

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Lister tous les projets
@router.get("/projects", response_model=list[ProjetOut])
def list_projects(db: Session = Depends(get_db)):
    return db.query(Projet).all()

# Obtenir un projet spécifique
@router.get("/projects/{id_projet}", response_model=ProjetOut)
def get_project(id_projet: str, db: Session = Depends(get_db)):
    project = db.query(Projet).filter(Projet.id_projet == id_projet).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    return project

# Créer un projet
@router.post("/projects", response_model=ProjetOut)
def create_project(project: ProjetCreate, db: Session = Depends(get_db)):
    db_project = Projet(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

# Lister les phases d’un projet
@router.get("/projects/{id_projet}/phases", response_model=list[PhaseOut])
def list_phases(id_projet: str, db: Session = Depends(get_db)):
    return db.query(Phase).filter(Phase.id_facture == id_projet).all()

# Ajouter une phase à un projet
@router.post("/projects/{id_projet}/phases", response_model=PhaseOut)
def add_phase(id_projet: str, phase: PhaseCreate, db: Session = Depends(get_db)):
    new_phase = Phase(**phase.dict())
    db.add(new_phase)
    db.commit()
    db.refresh(new_phase)
    return new_phase
