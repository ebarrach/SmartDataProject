from fastapi import APIRouter, Depends
from ..auth import get_current_user
from ..schemas import PersonnelOut

router = APIRouter()

@router.get("/me", response_model=PersonnelOut)
def get_profile(current_user: PersonnelOut = Depends(get_current_user)):
    return current_user