# ============================================
# IMPORTS
# ============================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Tache, Facture
from app.schemas import TacheCreate, TacheOut
from app.auth import get_current_user


# ============================================
# ROUTER INITIALIZATION
# ============================================

router = APIRouter()

# ============================================
# ROUTE : List all tasks
# ============================================

@router.get("/tasks", response_model=list[TacheOut])
def list_tasks(db: Session = Depends(get_db)):
    """Returns all tasks stored in the database.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
    return db.query(Tache).all()

# ============================================
# ROUTE : Get a task by ID
# ============================================

@router.get("/tasks/{id_tache}", response_model=TacheOut)
def get_task(id_tache: str, db: Session = Depends(get_db)):
    """Returns a task based on its ID.
    Raises 404 if not found.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
    task = db.query(Tache).filter(Tache.id_tache == id_tache).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# ============================================
# ROUTE : Create a new task
# ============================================

@router.post("/tasks", response_model=TacheOut)
def create_task(task: TacheCreate, db: Session = Depends(get_db)):
    """Creates and stores a new task.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
    db_task = Tache(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

# ============================================
# ROUTE : Update an existing task
# ============================================

@router.put("/tasks/{id_tache}", response_model=TacheOut)
def update_task(id_tache: str, updated_task: TacheCreate, db: Session = Depends(get_db)):
    """Updates an existing task with new values.
    Raises 404 if not found.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
    task = db.query(Tache).filter(Tache.id_tache == id_tache).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in updated_task.dict().items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task

# ============================================
# ROUTE : Delete a task
# ============================================

@router.delete("/tasks/{id_tache}")
def delete_task(id_tache: str, db: Session = Depends(get_db)):
    """Deletes a task from the database.
    Raises 404 if the task is not found.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
    task = db.query(Tache).filter(Tache.id_tache == id_tache).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"message": "Task successfully deleted"}

# ============================================
# ROUTE : Delete a facture (duplicate cleanup)
# ============================================

@router.delete("/factures/{id_facture}")
def delete_facture(id_facture: str, db: Session = Depends(get_db)):
    """Deletes a facture with error handling.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.2 22/06/2025)
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

# ============================================
# ROUTE : Récupérer les tâches pour l’agenda
# ============================================

@router.get("/tasks/agenda")
def get_agenda_tasks(user=Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Retourne une liste simplifiée de tâches à afficher dans la colonne agenda.

    Version:
    --------
    specification: Esteban Barracho (v.1 11/07/2025)
    implement: Esteban Barracho (v.1 11/07/2025)
    """
    tasks = db.query(Tache).filter(Tache.statut.in_(["planifiée", "à faire"])).all()
    return [{"id": t.id_tache, "nom_tache": t.nom_tache} for t in tasks]
