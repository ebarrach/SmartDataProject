# ============================================
# IMPORTS
# ============================================


from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db


# ============================================
# ROUTER INITIALIZATION
# ============================================

router = APIRouter(prefix="/api/finance", tags=["Finance"])

# =============================
# Dépassements par projet
# =============================

@router.get("/depassements")
def get_depassements(db: Session = Depends(get_db)):
    """Retrieves the total number of exceeded hours (heures_depassees) per project.
    Parameters:
    -----------
    db (Session): Active database session used for executing SQL queries.

    Returns:
    --------
    dict: A dictionary with two lists:
        - 'labels': List of project IDs.
        - 'data': Corresponding list of exceeded hours (as floats).

    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 21/06/2025)
    """
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
    """Retrieves the number of delayed tasks (alerte_retard = 1) per project.
    Parameters:
    -----------
    db (Session): Active database session used for executing SQL queries.

    Returns:
    --------
    dict: A dictionary with:
        - 'labels': List of project IDs.
        - 'data': Corresponding number of alert-triggering tasks.

    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 21/06/2025)
    """
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
    """Retrieves both estimated budgets and real computed costs per project.
    Parameters:
    -----------
    db (Session): Active database session used for executing SQL queries.

    Returns:
    --------
    dict: A dictionary containing:
        - 'labels': List of project IDs.
        - 'budget': List of estimated budget values.
        - 'cout': List of actual cost values.

    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 21/06/2025)
    """
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
