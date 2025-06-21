# ============================================
# IMPORTS
# ============================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Client

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
# ROUTE : List All Clients
# ============================================

@router.get("/clients")
def list_clients(db: Session = Depends(get_db)):
    """Retrieves all registered clients from the database.
    Parameters:
    -----------
    db (Session): Database session provided by dependency.
    Returns:
    --------
    list[Client]: List of client records.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    return db.query(Client).all()
