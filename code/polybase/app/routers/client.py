# ============================================
# IMPORTS
# ============================================

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Client, Facture
from ..schemas import ClientOut

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

# ============================================
# ROUTE : Create New Client
# ============================================

@router.post("/clients", response_model=ClientOut)
def create_client(client: ClientOut = Body(...), db: Session = Depends(get_db)):
    """Creates a new client entry in the database.

    Parameters:
    -----------
    client (ClientOut): Client data from request body.
    db (Session): Database session provided by dependency.

    Returns:
    --------
    ClientOut: Newly created client record.

    Version:
    --------
    specification: Esteban Barracho (v.1 21/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """
    if db.query(Client).filter(Client.id_client == client.id_client).first():
        raise HTTPException(status_code=400, detail="Client ID already exists")

    db_client = Client(**client.dict())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

# ============================================
# ROUTE : Delete Client
# ============================================

@router.delete("/clients/{id_client}")
def delete_client(id_client: str, db: Session = Depends(get_db)):
    """Deletes a client from the database if it exists.

    Parameters:
    -----------
    id_client (str): ID of the client to delete.
    db (Session): Active database session.

    Returns:
    --------
    dict: Confirmation message if deletion is successful.

    Raises:
    -------
    HTTPException: If the client is not found.

    Version:
    --------
    specification: Esteban Barracho (v.1 21/06/2025)
    implement: Esteban Barracho (v.1 21/06/2025)
    """
    client = db.query(Client).filter(Client.id_client == id_client).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    db.delete(client)
    db.commit()
    return {"message": f"Client {id_client} deleted successfully"}

# ============================================
# ROUTE : Delete Facture
# ============================================

@router.delete("/factures/{id_facture}")
def delete_facture(id_facture: str, db: Session = Depends(get_db)):
    """Deletes a facture if found.

    Parameters:
    -----------
    id_facture (str): ID of the facture to delete.
    db (Session): Database session.

    Returns:
    --------
    dict: Confirmation message or error.

    Version:
    --------
    specification: Esteban Barracho (v.1 21/06/2025)
    implement: Esteban Barracho (v.2 22/06/2025)
    """
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

@router.delete("/clients/{id_client}")
def delete_client(id_client: str, db: Session = Depends(get_db)):
    """
    Deletes a client entry from the database based on its identifier.

    Parameters:
    -----------
    id_client (str): Unique identifier of the client to delete.
    db (Session): Database session provided by dependency injection.

    Returns:
    --------
    dict: Confirmation message upon successful deletion.

    Version:
    --------
    specification: Esteban Barracho (v.1 26/06/2025)
    implement: Esteban Barracho (v.1 09/07/2025)
    """
    client = db.query(Client).filter(Client.id_client == id_client).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    db.delete(client)
    db.commit()
    return {"message": f"Client {id_client} deleted successfully"}

