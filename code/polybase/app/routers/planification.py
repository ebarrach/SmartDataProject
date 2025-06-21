from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import PlanificationCollaborateur
from ..schemas import PlanificationCreate, PlanificationOut

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/planifications", response_model=list[PlanificationOut])
def list_planifications(db: Session = Depends(get_db)):
    return db.query(PlanificationCollaborateur).all()

@router.get("/planifications/{id_planification}", response_model=PlanificationOut)
def get_planification(id_planification: str, db: Session = Depends(get_db)):
    plan = db.query(PlanificationCollaborateur).filter(PlanificationCollaborateur.id_planification == id_planification).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Planification non trouvée")
    return plan

@router.post("/planifications", response_model=PlanificationOut)
def create_planification(plan: PlanificationCreate, db: Session = Depends(get_db)):
    db_plan = PlanificationCollaborateur(**plan.dict())
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

@router.put("/planifications/{id_planification}", response_model=PlanificationOut)
def update_planification(id_planification: str, plan_update: PlanificationCreate, db: Session = Depends(get_db)):
    plan = db.query(PlanificationCollaborateur).filter(PlanificationCollaborateur.id_planification == id_planification).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Planification non trouvée")
    for key, value in plan_update.dict().items():
        setattr(plan, key, value)
    db.commit()
    db.refresh(plan)
    return plan

@router.delete("/planifications/{id_planification}")
def delete_planification(id_planification: str, db: Session = Depends(get_db)):
    plan = db.query(PlanificationCollaborateur).filter(PlanificationCollaborateur.id_planification == id_planification).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Planification non trouvée")
    db.delete(plan)
    db.commit()
    return {"message": "Planification supprimée avec succès"}
