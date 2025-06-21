from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal

router = APIRouter()

@router.get("/multiplicating-factor/{honoraire}/{cout}")
def get_multiplicating_factor(honoraire: float, cout: float):
    # seuil à définir
    if cout == 0:
        raise HTTPException(400, detail="Coût ne peut pas être nul")
    return {"multiplicating_factor": round(honoraire / cout, 2)}