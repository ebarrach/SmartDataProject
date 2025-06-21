# ============================================
# IMPORTS
# ============================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Tache
from ..schemas import TacheCreate, TacheOut

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
