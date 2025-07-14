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
    """Returns the authenticated user's profile based on session.
    Parameters:
    -----------
    current_user : PersonnelOut
        The user retrieved from session using dependency injection.
    Returns:
    --------
    PersonnelOut
        The structured profile of the currently authenticated user.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
    assert isinstance(current_user, PersonnelOut), "Utilisateur authentifié invalide (PersonnelOut attendu)"
    return current_user
