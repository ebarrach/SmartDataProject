# ============================================
# ROUTES - FINANCIAL DASHBOARD
# ============================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(prefix="/api/finance", tags=["Finance"])

# =============================
# Dépassements par projet
# =============================

@router.get("/depassements")
def get_depassements(db: Session = Depends(get_db)):
    """Returns a list of hours exceeded per project."""
    result = db.execute("""
                        SELECT p.id_projet, SUM(t.heures_depassees) AS total
                        FROM Projet p
                                 JOIN Tache t ON p.id_projet = t.id_projet
                        WHERE t.heures_depassees > 0
                        GROUP BY p.id_projet
                        """).fetchall()

    return {
        "labels": [row[0] for row in result],
        "data": [float(row[1]) for row in result]
    }


# =============================
# Alertes en cours (retards)
# =============================

@router.get("/alertes")
def get_alertes(db: Session = Depends(get_db)):
    """Returns number of delayed tasks per project."""
    result = db.execute("""
                        SELECT p.id_projet, COUNT(*) AS nb_alertes
                        FROM Tache t
                                 JOIN Projet p ON t.id_projet = p.id_projet
                        WHERE t.alerte_retard = 1
                        GROUP BY p.id_projet
                        """).fetchall()

    return {
        "labels": [row[0] for row in result],
        "data": [row[1] for row in result]
    }


# =============================
# Budgets vs Coûts
# =============================

@router.get("/budgets")
def get_budget_vs_couts(db: Session = Depends(get_db)):
    """Returns both budgets and real costs per project."""
    result = db.execute("""
                        SELECT p.id_projet, p.budget_estime, SUM(t.heures_prestees * p.taux_horaire) AS cout
                        FROM Projet p
                                 JOIN Tache t ON t.id_projet = p.id_projet
                                 JOIN Prestation pr ON pr.id_tache = t.id_tache
                        GROUP BY p.id_projet, p.budget_estime
                        """).fetchall()

    return {
        "labels": [row[0] for row in result],
        "budget": [float(row[1]) for row in result],
        "cout": [float(row[2]) for row in result]
    }
