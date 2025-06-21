from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import SessionLocal
from ..auth import get_current_user
from ..models import Tache, PlanificationCollaborateur, ProjectionFacturation

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/dashboard/tasks/alertes")
def taches_en_alerte(db: Session = Depends(get_db)):
    en_retard = db.query(Tache).filter(Tache.alerte_retard == True).count()
    return {"taches_retard": en_retard}

@router.get("/dashboard/heures-depassees")
def total_depassement_heures(db: Session = Depends(get_db)):
    result = db.query(func.sum(Tache.heures_depassees)).scalar()
    return {"heures_depassees_totales": float(result or 0)}

@router.get("/dashboard/facturation")
def synthese_facturation(db: Session = Depends(get_db)):
    projets = db.query(
        ProjectionFacturation.id_projet,
        func.sum(ProjectionFacturation.montant_projete).label("total_projete"),
        func.sum(ProjectionFacturation.montant_facturable_actuel).label("total_actuel")
    ).group_by(ProjectionFacturation.id_projet).all()

    return [
        {
            "id_projet": p.id_projet,
            "montant_projete": float(p.total_projete),
            "montant_facturable_actuel": float(p.total_actuel),
            "ecart": float(p.total_projete - p.total_actuel)
        }
        for p in projets
    ]

@router.get("/dashboard/mes-taches")
def mes_taches(user=Depends(get_current_user), db: Session = Depends(get_db)):
    taches = db.query(Tache).join(PlanificationCollaborateur).filter(
        PlanificationCollaborateur.id_collaborateur == user.id_personnel,
        Tache.statut != "terminé"
    ).all()

    return [
        {
            "id_tache": t.id_tache,
            "nom": t.nom_tache,
            "statut": t.statut,
            "debut": str(t.date_debut),
            "fin": str(t.date_fin)
        }
        for t in taches
    ]
