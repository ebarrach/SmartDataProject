from pydantic import BaseModel

class PersonnelOut(BaseModel):
    id_personnel: str
    nom: str
    prenom: str
    email: str
    fonction: str

    class Config:
        orm_mode = True