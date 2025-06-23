# ============================================
# IMPORTS
# ============================================

from fastapi import APIRouter, Depends
from app.auth import get_current_user
from app.schemas import PersonnelOut

# ============================================
# ROUTER INITIALIZATION
# ============================================

router = APIRouter()

# ============================================
# ROUTE : GET CURRENT USER'S PROFILE
# ============================================

@router.get("/me", response_model=PersonnelOut)
def get_profile(current_user: PersonnelOut = Depends(get_current_user)):
    """
    Returns the authenticated user's profile based on session.

    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
    return current_user
