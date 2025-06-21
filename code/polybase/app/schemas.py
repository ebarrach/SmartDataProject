from pydantic import BaseModel
from typing import Optional
from datetime import date

# === PROJET ===
class ProjetCreate(BaseModel):
    id_projet: str
    nom_projet: str
    statut: str
    date_debut: date
    date_fin: date
    montant_total_estime: float
    type_marche: str
    id_client: str

class ProjetOut(ProjetCreate):
    class Config:
        orm_mode = True

# === PHASE ===
class PhaseCreate(BaseModel):
    id_phase: str
    nom_phase: str
    ordre_phase: int
    montant_phase: float
    id_facture: Optional[str] = None

class PhaseOut(PhaseCreate):
    class Config:
        orm_mode = True

# === TACHE ===
class TacheCreate(BaseModel):
    id_tache: str
    id_phase: str
    nom_tache: str
    description: str
    alerte_retard: bool
    conges_integres: bool
    statut: str
    est_realisable: bool
    date_debut: date
    date_fin: date

class TacheOut(TacheCreate):
    class Config:
        orm_mode = True

# === CLIENT ===
class ClientOut(BaseModel):
    id_client: str
    nom_client: str
    adresse: str
    secteur_activite: str

    class Config:
        orm_mode = True

# === PERSONNEL ===
class PersonnelOut(BaseModel):
    id_personnel: str
    nom: str
    prenom: str
    email: str
    fonction: str

    class Config:
        orm_mode = True

# === FACTURE ===
class FactureOut(BaseModel):
    id_facture: str
    date_emission: date
    montant_facture: float
    transmission_electronique: bool
    annexe: str
    statut: str
    reference_banque: str
    fichier_facture: str

    class Config:
        orm_mode = True

# === PLANIFICATION COLLABORATEUR ===
class PlanificationCreate(BaseModel):
    id_planification: str
    id_tache: str
    id_collaborateur: str
    heures_disponibles: float
    alerte_depassement: bool
    semaine: str
    heures_prevues: float

class PlanificationOut(PlanificationCreate):
    class Config:
        orm_mode = True

# === PRESTATION COLLABORATEUR ===
class PrestationCreate(BaseModel):
    id_prestation: str
    date: date
    id_tache: str
    id_collaborateur: str
    heures_effectuees: float
    mode_facturation: str
    facture_associee: Optional[str]
    taux_horaire: float
    commentaire: str

class PrestationOut(PrestationCreate):
    class Config:
        orm_mode = True

# === COUT ===
class CoutOut(BaseModel):
    id_cout: str
    type_cout: str
    montant: float
    nature_cout: str
    date: date
    source: str

    class Config:
        orm_mode = True

# === PROJECTION FACTURATION ===
class ProjectionFacturationOut(BaseModel):
    id_projection: str
    mois: str
    montant_projete: float
    montant_facturable_actuel: float
    seuil_minimal: float
    alerte_facturation: bool
    id_projet: str

    class Config:
        orm_mode = True

# === IMPORT LOG ===
class ImportLogOut(BaseModel):
    id_import: str
    source: str
    type_donnee: str
    date_import: date
    statut: str
    message_log: str

    class Config:
        orm_mode = True
