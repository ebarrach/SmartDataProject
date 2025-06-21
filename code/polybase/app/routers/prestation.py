from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import PrestationCollaborateur
from ..schemas import PrestationCreate, PrestationOut

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/prestation", response_model=list[PrestationOut])
def list_prestations(db: Session = Depends(get_db)):
    return db.query(PrestationCollaborateur).all()

@router.get("/prestation/{id_prestation}", response_model=PrestationOut)
def get_prestation(id_prestation: str, db: Session = Depends(get_db)):
    prestation = db.query(PrestationCollaborateur).filter(PrestationCollaborateur.id_prestation == id_prestation).first()
    if not prestation:
        raise HTTPException(status_code=404, detail="Prestation non trouvée")
    return prestation

@router.post("/prestation", response_model=PrestationOut)
def create_prestation(prestation: PrestationCreate, db: Session = Depends(get_db)):
    db_prestation = PrestationCollaborateur(**prestation.dict())
    db.add(db_prestation)
    db.commit()
    db.refresh(db_prestation)
    return db_prestation

@router.put("/prestation/{id_prestation}", response_model=PrestationOut)
def update_prestation(id_prestation: str, updated: PrestationCreate, db: Session = Depends(get_db)):
    prestation = db.query(PrestationCollaborateur).filter(PrestationCollaborateur.id_prestation == id_prestation).first()
    if not prestation:
        raise HTTPException(status_code=404, detail="Prestation non trouvée")
    for key, value in updated.dict().items():
        setattr(prestation, key, value)
    db.commit()
    db.refresh(prestation)
    return prestation

@router.delete("/prestation/{id_prestation}")
def delete_prestation(id_prestation: str, db: Session = Depends(get_db)):
    prestation = db.query(PrestationCollaborateur).filter(PrestationCollaborateur.id_prestation == id_prestation).first()
    if not prestation:
        raise HTTPException(status_code=404, detail="Prestation non trouvée")
    db.delete(prestation)
    db.commit()
    return {"message": "Prestation supprimée avec succès"}
