# ============================================
# IMPORTS
# ============================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import SessionLocal
from app.auth import get_current_user
from app.models import Tache, PlanificationCollaborateur, ProjectionFacturation

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
# ROUTE : Count tasks with delay alert
# ============================================

@router.get("/dashboard/tasks/alertes")
def taches_en_alerte(db: Session = Depends(get_db)):
    """Returns the number of tasks marked with a delay alert.
    Parameters:
    -----------
    db (Session): Database session.
    Returns:
    --------
    dict: { "taches_retard": <count> }
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
    en_retard = db.query(Tache).filter(Tache.alerte_retard == True).count()
    return {"taches_retard": en_retard}

# ============================================
# ROUTE : Sum of exceeded hours
# ============================================

@router.get("/dashboard/heures-depassees")
def total_depassement_heures(db: Session = Depends(get_db)):
    """Returns the total number of exceeded hours across all tasks.
    Parameters:
    -----------
    db (Session): Database session.
    Returns:
    --------
    dict: { "heures_depassees_totales": <sum> }
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
    result = db.query(func.sum(Tache.heures_depassees)).scalar()
    return {"heures_depassees_totales": float(result or 0)}

# ============================================
# ROUTE : Billing projection summary
# ============================================

@router.get("/dashboard/facturation")
def synthese_facturation(db: Session = Depends(get_db)):
    """Returns a summary of projected vs. actual billable amounts by project.
    Parameters:
    -----------
    db (Session): Database session.
    Returns:
    --------
    list[dict]: List of project-level billing summaries.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
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

# ============================================
# ROUTE : Current user’s active tasks
# ============================================

@router.get("/dashboard/mes-taches")
def mes_taches(user=Depends(get_current_user), db: Session = Depends(get_db)):
    """Returns all non-completed tasks assigned to the current user.
    Parameters:
    -----------
    user: The authenticated user.
    db (Session): Database session.
    Returns:
    --------
    list[dict]: List of task data assigned to the user.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
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
