# ============================================
# IMPORTS
# ============================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import PlanificationCollaborateur
from ..schemas import PlanificationCreate, PlanificationOut

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
# ROUTE : List all planifications
# ============================================

@router.get("/planifications", response_model=list[PlanificationOut])
def list_planifications(db: Session = Depends(get_db)):
    """Returns all collaborator task planifications.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    return db.query(PlanificationCollaborateur).all()

# ============================================
# ROUTE : Get one planification by ID
# ============================================

@router.get("/planifications/{id_planification}", response_model=PlanificationOut)
def get_planification(id_planification: str, db: Session = Depends(get_db)):
    """Returns a specific planification by ID.
    Raises 404 if not found.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    plan = db.query(PlanificationCollaborateur).filter(
        PlanificationCollaborateur.id_planification == id_planification
    ).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Planification not found")
    return plan

# ============================================
# ROUTE : Create a new planification
# ============================================

@router.post("/planifications", response_model=PlanificationOut)
def create_planification(plan: PlanificationCreate, db: Session = Depends(get_db)):
    """Creates and stores a new planification entry.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    db_plan = PlanificationCollaborateur(**plan.dict())
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

# ============================================
# ROUTE : Update an existing planification
# ============================================

@router.put("/planifications/{id_planification}", response_model=PlanificationOut)
def update_planification(id_planification: str, plan_update: PlanificationCreate, db: Session = Depends(get_db)):
    """Updates an existing planification entry.
    Raises 404 if not found.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    plan = db.query(PlanificationCollaborateur).filter(
        PlanificationCollaborateur.id_planification == id_planification
    ).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Planification not found")
    for key, value in plan_update.dict().items():
        setattr(plan, key, value)
    db.commit()
    db.refresh(plan)
    return plan

# ============================================
# ROUTE : Delete a planification
# ============================================

@router.delete("/planifications/{id_planification}")
def delete_planification(id_planification: str, db: Session = Depends(get_db)):
    """Deletes a planification from the database.
    Raises 404 if not found.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    plan = db.query(PlanificationCollaborateur).filter(
        PlanificationCollaborateur.id_planification == id_planification
    ).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Planification not found")
    db.delete(plan)
    db.commit()
    return {"message": "Planification successfully deleted"}
