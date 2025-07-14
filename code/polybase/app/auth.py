# ============================================
# IMPORTS
# ============================================

import bcrypt
from fastapi import Depends, HTTPException, Cookie
from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import Personnel

# ============================================
# DATABASE - SESSION
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
# USER AUTHENTICATION
# ============================================

def authenticate_user(email: str, plain_password: str, db: Session):
    """This function attempts to authenticate a user via their email and password.
    Parameter:
    ----------
    email (str): The user's email address.
    Plain_password (str): The password entered by the user.
    Db (Session): The active database session.
    Return:
    -------
    (Personnel | None): Returns the user if authenticated, else None.
    Version:
    --------
    specification: Esteban Barracho (v.2 23/06/25)
    implement: Esteban Barracho (v.2 23/06/25)
    """
    assert isinstance(email, str) and email, "Email invalide"
    assert isinstance(plain_password, str) and plain_password, "Mot de passe invalide"
    assert db, "Session DB invalide"

    user = db.query(Personnel).filter(Personnel.email == email).first()
    if not user or not user.password:
        return None
    if not bcrypt.checkpw(plain_password.encode('utf-8'), user.password.encode('utf-8')):
        return None
    return user

# ============================================
# REGULAR USER (via COOKIE)
# ============================================

def get_current_user(session_id: str = Cookie(None), db: Session = Depends(get_db)):
    """This function retrieves the currently authenticated user from the session cookie.
    Parameter:
    ----------
    session_id (str): The session ID stored in the user's cookies.
    Db (Session): The active database session.
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
    if not session_id or not isinstance(session_id, str):
        raise HTTPException(status_code=401, detail="Session non trouvée")
    assert db, "Session DB invalide"
    user = db.query(Personnel).filter(Personnel.id_personnel == session_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
    return user
