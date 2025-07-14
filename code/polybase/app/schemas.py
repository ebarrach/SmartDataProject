# ============================================
# IMPORTS
# ============================================

from pydantic import BaseModel
from typing import Optional
from datetime import date

# ============================================
# SCHEMAS: PROJECT
# ============================================

class ProjetCreate(BaseModel):
    """Schema for creating a project.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    id_projet: str
    nom_projet: str
    statut: str
    date_debut: date
    date_fin: date
    montant_total_estime: float
    type_marche: str
    id_client: str

class ProjetOut(ProjetCreate):
    """Schema for returning a project (ORM-enabled).
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    class Config:
        orm_mode = True

# ============================================
# SCHEMAS: PHASE
# ============================================

class PhaseCreate(BaseModel):
    """Schema for creating a phase.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    id_phase: str
    nom_phase: str
    ordre_phase: int
    montant_phase: float
    id_facture: Optional[str] = None

class PhaseOut(PhaseCreate):
    """Schema for returning a phase (ORM-enabled).
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    class Config:
        orm_mode = True

# ============================================
# SCHEMAS: TASK
# ============================================

class TacheCreate(BaseModel):
    """Schema for creating a task.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

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
    """Schema for returning a task (ORM-enabled).
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    class Config:
        orm_mode = True

# ============================================
# SCHEMAS: CLIENT
# ============================================

class ClientCreate(BaseModel):
    """Schema for creating a client.
    Version:
    --------
    specification: Esteban Barracho (v.1 22/06/2025)
    implement: Esteban Barracho (v.1 22/06/2025)
    """
    id_client: str
    nom_client: str
    adresse: str
    secteur_activite: str

class ClientOut(BaseModel):
    """Schema for returning a client.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    id_client: str
    nom_client: str
    adresse: str
    secteur_activite: str

    class Config:
        orm_mode = True

# ============================================
# SCHEMAS: PERSONNEL
# ============================================

class PersonnelCreate(BaseModel):
    """Schema for creating personnel.
    Version:
    --------
    specification: Esteban Barracho (v.1 22/06/2025)
    implement: Esteban Barracho (v.1 22/06/2025)
    """
    id_personnel: str
    nom: str
    prenom: str
    email: str
    fonction: str

class PersonnelOut(BaseModel):
    """Schema for returning personnel data.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    id_personnel: str
    nom: str
    prenom: str
    email: str
    fonction: str

    class Config:
        orm_mode = True

# ============================================
# SCHEMAS: INVOICE
# ============================================

class FactureOut(BaseModel):
    """Schema for returning invoice data.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

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

# ============================================
# SCHEMAS: TASK PLANNING
# ============================================

class PlanificationCreate(BaseModel):
    """Schema for creating a collaborator task planning.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    id_planification: str
    id_tache: str
    id_collaborateur: str
    heures_disponibles: float
    alerte_depassement: bool
    semaine: str
    heures_prevues: float

class PlanificationOut(PlanificationCreate):
    """Schema for returning a task planning (ORM-enabled).
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    class Config:
        orm_mode = True

# ============================================
# SCHEMAS: TASK PERFORMANCE
# ============================================

class PrestationCreate(BaseModel):
    """Schema for creating a collaborator performance log.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    id_prestation: str
    id_projet: Optional[str] = None
    date: date
    id_tache: str
    id_collaborateur: str
    heures_effectuees: float
    mode_facturation: str
    facture_associee: Optional[str]
    taux_horaire: float
    commentaire: str

class PrestationOut(PrestationCreate):
    """Schema for returning a performance log (ORM-enabled).
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    class Config:
        orm_mode = True

# ============================================
# SCHEMAS: COST
# ============================================
class CoutCreate(BaseModel):
    """Schema for creating a cost.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.2 26/06/2025)
    """
    id_cout: str
    type_cout: str
    montant: float
    nature_cout: str
    date: date
    source: str
    id_projet: Optional[str] = None

class CoutOut(BaseModel):
    """Schema for returning cost data.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.2 26/06/2025)
    """
    id_cout: str
    type_cout: str
    montant: float
    nature_cout: str
    date: date
    source: str
    id_projet: Optional[str] = None

    class Config:
        orm_mode = True

# ============================================
# SCHEMAS: BILLING PROJECTION
# ============================================

class ProjectionFacturationCreate(BaseModel):
    """Schema for creating or updating a billing projection.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.2 21/06/2025)
    """
    id_projection: str
    mois: str
    montant_projete: float
    montant_facturable_actuel: float
    seuil_minimal: float
    alerte_facturation: bool
    id_projet: str
    est_certain: Optional[bool] = True

class ProjectionFacturationOut(ProjectionFacturationCreate):
    """Schema for returning billing projection (ORM-enabled).
    Version:
    --------
    specification: Esteban Barracho (v.1 21/06/2025)
    implement: Esteban Barracho (v.1 21/06/2025)
    """
    class Config:
        orm_mode = True

# ============================================
# SCHEMAS: HONORAIRE REPARTI
# ============================================

class HonoraireRepartiCreate(BaseModel):
    """Schema for creating a repartition of honoraires.
    Version:
    --------
    specification: Esteban Barracho (v.1 21/06/2025)
    implement: Esteban Barracho (v.1 21/06/2025)
    """
    id_repartition: str
    id_projet: str
    societe: str
    montant: float

class HonoraireRepartiOut(HonoraireRepartiCreate):
    """Schema for returning honoraires repartis (ORM-enabled).
    Version:
    --------
    specification: Esteban Barracho (v.1 21/06/2025)
    implement: Esteban Barracho (v.1 22/06/2025)
    """
    class Config:
        orm_mode = True

# ============================================
# SCHEMAS: IMPORT LOG
# ============================================

class ImportLogCreate(BaseModel):
    """Schema for creating an import log.
    Version:
    --------
    specification: Esteban Barracho (v.2 26/06/2025)
    implement: Esteban Barracho (v.2 26/06/2025)
    """
    id_import: str
    source: str
    type_donnee: str
    date_import: date
    statut: str
    message_log: str
    id_projet: Optional[str] = None

class ImportLogOut(BaseModel):
    """Schema for returning import log information.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.2 26/06/2025)
    """
    id_import: str
    source: str
    type_donnee: str
    date_import: date
    statut: str
    message_log: str
    id_projet: Optional[str] = None
    class Config:
        orm_mode = True


# ============================================
# SCHEMAS: OFFRE
# ============================================

class OffreCreate(BaseModel):
    """Schema for creating an 'Offre' entry.
    Version:
    --------
    specification: Esteban Barracho (v.1 24/06/2025)
    implement: Esteban Barracho (v.2 26/06/2025)
    """
    id_offre: str
    annee: int
    entite: str
    type_marche: str
    nombre: int
    indicateur: Optional[str] = None
    id_client: Optional[str] = None

class OffreOut(OffreCreate):
    """Schema for returning an 'Offre' entry (ORM-enabled).
    Version:
    --------
    specification: Esteban Barracho (v.1 24/06/2025)
    implement: Esteban Barracho (v.1 24/06/2025)
    """
    class Config:
        orm_mode = True
