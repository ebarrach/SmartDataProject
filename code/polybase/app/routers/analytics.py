# ============================================
# IMPORTS
# ============================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal

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
