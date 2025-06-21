from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Tache
from ..schemas import TacheCreate, TacheOut

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Lister toutes les tâches
@router.get("/tasks", response_model=list[TacheOut])
def list_tasks(db: Session = Depends(get_db)):
    return db.query(Tache).all()

# Obtenir une tâche spécifique
@router.get("/tasks/{id_tache}", response_model=TacheOut)
def get_task(id_tache: str, db: Session = Depends(get_db)):
    task = db.query(Tache).filter(Tache.id_tache == id_tache).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tâche non trouvée")
    return task

# Créer une tâche
@router.post("/tasks", response_model=TacheOut)
def create_task(task: TacheCreate, db: Session = Depends(get_db)):
    db_task = Tache(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

# Mettre à jour une tâche
@router.put("/tasks/{id_tache}", response_model=TacheOut)
def update_task(id_tache: str, updated_task: TacheCreate, db: Session = Depends(get_db)):
    task = db.query(Tache).filter(Tache.id_tache == id_tache).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tâche non trouvée")
    for key, value in updated_task.dict().items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task

# Supprimer une tâche
@router.delete("/tasks/{id_tache}")
def delete_task(id_tache: str, db: Session = Depends(get_db)):
    task = db.query(Tache).filter(Tache.id_tache == id_tache).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tâche non trouvée")
    db.delete(task)
    db.commit()
    return {"message": "Tâche supprimée avec succès"}
