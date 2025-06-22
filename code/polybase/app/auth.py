# ============================================
# IMPORTS
# ============================================

from fastapi import Depends, HTTPException, Cookie
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Personnel

# ============================================
# BASE DE DONNÉES - SESSION
# ============================================

def get_db():
    """This function provides a database session.
    Return:
    -------
    (Session): A SQLAlchemy session instance.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/25)
    implement: Esteban Barracho (v.1 19/06/25)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================
# AUTHENTIFICATION UTILISATEUR
# ============================================

def authenticate_user(email: str, db: Session):
    """This function attempts to authenticate a user via their email.
    Parameter:
    ----------
    email (str): The user's email address.
    db (Session): The active database session.
    Return:
    -------
    (Personnel | None): Returns the user if found, else None.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/25)
    implement: Esteban Barracho (v.1 19/06/25)
    """
    user = db.query(Personnel).filter(Personnel.email == email).first()
    return user

# ============================================
# UTILISATEUR COURANT (via COOKIE)
# ============================================

def get_current_user(session_id: str = Cookie(None), db: Session = Depends(get_db)):
    """This function retrieves the currently authenticated user from the session cookie.
    Parameter:
    ----------
    session_id (str): The session ID stored in the user's cookies.
    db (Session): The active database session.
    Return:
    -------
    (Personnel): The authenticated user object.
    Raise:
    ------
    HTTPException: If no session or user is found.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/25)
    implement: Esteban Barracho (v.1 19/06/25)
    """
    if not session_id:
        raise HTTPException(status_code=401, detail="Session non trouvée")
    user = db.query(Personnel).filter(Personnel.id_personnel == session_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
    return user
