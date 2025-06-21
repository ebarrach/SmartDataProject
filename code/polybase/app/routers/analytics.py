# ============================================
# IMPORTS
# ============================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models import ProjectionFacturation, PlanificationCollaborateur, Facture
from ..database import SessionLocal
from ..models import HonoraireReparti
from ..schemas import HonoraireRepartiCreate, ProjectionFacturationCreate, ProjectionFacturationOut

# ============================================
# DATABASE DEPENDENCY
# ============================================

from ..database import SessionLocal

def get_db():
    """Provides a database session for dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================
# ROUTER INITIALIZATION
# ============================================

router = APIRouter()

# ============================================
# ROUTE : Multiplicating Factor Calculation
# ============================================

@router.get("/multiplicating-factor/{honoraire}/{cout}")
def get_multiplicating_factor(honoraire: float, cout: float):
    """This endpoint calculates the multiplicating factor (honoraire / cout).
    Parameters:
    -----------
    honoraire (float): The standard hourly rate.
    cout (float): The reference cost value.
    Returns:
    --------
    dict: Contains the calculated multiplicating factor (rounded to 2 decimals).
    Raises:
    -------
    HTTPException: If cost is zero to avoid division by zero.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    if cout == 0:
        raise HTTPException(400, detail="Cost cannot be zero")
    return {"multiplicating_factor": round(honoraire / cout, 2)}


@router.delete("/projection_facturation/{id_projection}")
def delete_projection(id_projection: str, db: Session = Depends(get_db)):
    """Deletes a billing projection entry.
    Raises 404 if not found.
    """
    projection = db.query(ProjectionFacturation).filter(
        ProjectionFacturation.id_projection == id_projection
    ).first()
    if not projection:
        raise HTTPException(status_code=404, detail="Projection not found")
    db.delete(projection)
    db.commit()
    return {"message": f"Projection {id_projection} deleted successfully"}

@router.delete("/factures/{id_facture}")
def delete_facture(id_facture: str, db: Session = Depends(get_db)):
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

@router.delete("/planifications/{id_planification}")
def delete_planification(id_planification: str, db: Session = Depends(get_db)):
    planif = db.query(PlanificationCollaborateur).filter(
        PlanificationCollaborateur.id_planification == id_planification
    ).first()
    if not planif:
        raise HTTPException(status_code=404, detail="Planification not found")
    db.delete(planif)
    db.commit()
    return {"message": f"Planification {id_planification} deleted successfully"}

@router.post("/analytics/honoraire")
def create_honoraire_reparti(entry: HonoraireRepartiCreate, db: Session = Depends(get_db)):
    """Creates an honoraire repartition for a given project.
    Version:
    --------
    specification: Esteban Barracho (v.1 21/06/2025)
    implement: Esteban Barracho (v.1 21/06/2025)
    """
    repartition = HonoraireReparti(**entry.dict())
    db.add(repartition)
    db.commit()
    return {"message": f"Honoraire {entry.id_repartition} added for project {entry.id_projet}"}


@router.put("/projection_facturation/{id_projection}", response_model=ProjectionFacturationOut)
def update_projection_facturation(id_projection: str, update: ProjectionFacturationCreate, db: Session = Depends(get_db)):
    """Updates a projection entry, including uncertainty status.
    Version:
    --------
    specification: Esteban Barracho (v.1 21/06/2025)
    implement: Esteban Barracho (v.1 21/06/2025)
    """
    proj = db.query(ProjectionFacturation).filter(ProjectionFacturation.id_projection == id_projection).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Projection not found")
    for key, value in update.dict().items():
        setattr(proj, key, value)
    db.commit()
    db.refresh(proj)
    return proj
