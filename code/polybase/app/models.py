# ============================================
# IMPORTS
# ============================================

from sqlalchemy import Column, String, Enum, Date, Boolean, DECIMAL, ForeignKey, Integer, Text
from .database import Base

# ============================================
# TABLE : PERSONNEL
# ============================================

class Personnel(Base):
    """ORM model for the 'Personnel' table.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    __tablename__ = "Personnel"
    id_personnel = Column(String(10), primary_key=True, index=True)
    type_personnel = Column(Enum("interne", "externe"))
    nom = Column(String(100))
    prenom = Column(String(100))
    email = Column(String(100))
    fonction = Column(String(100))
    taux_honoraire_standard = Column(DECIMAL(8, 2))

# ============================================
# TABLE : RESPONSABLE PROJET
# ============================================

class ResponsableProjet(Base):
    """ORM model for the 'ResponsableProjet' table.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    __tablename__ = "ResponsableProjet"
    id_personnel = Column(String(10), ForeignKey("Personnel.id_personnel"), primary_key=True)
    niveau_hierarchique = Column(String(50))

# ============================================
# TABLE : CLIENT
# ============================================

class Client(Base):
    """ORM model for the 'Client' table.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    __tablename__ = "Client"
    id_client = Column(String(10), primary_key=True)
    nom_client = Column(String(100))
    adresse = Column(Text)
    secteur_activite = Column(String(100))

# ============================================
# TABLE : COLLABORATEUR
# ============================================

class Collaborateur(Base):
    """ORM model for the 'Collaborateur' table.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    __tablename__ = "Collaborateur"
    id_personnel = Column(String(10), ForeignKey("Personnel.id_personnel"), primary_key=True)

# ============================================
# TABLE : FACTURE
# ============================================

class Facture(Base):
    """ORM model for the 'Facture' table.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    __tablename__ = "Facture"
    id_facture = Column(String(10), primary_key=True)
    date_emission = Column(Date)
    montant_facture = Column(DECIMAL(10, 2))
    transmission_electronique = Column(Boolean)
    annexe = Column(Text)
    statut = Column(Enum("émise", "payée", "en attente"))
    reference_banque = Column(String(100))
    fichier_facture = Column(Text)

# ============================================
# TABLE : PHASE
# ============================================

class Phase(Base):
    """ORM model for the 'Phase' table.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    __tablename__ = "Phase"
    id_phase = Column(String(10), primary_key=True)
    nom_phase = Column(String(100))
    ordre_phase = Column(Integer)
    montant_phase = Column(DECIMAL(10, 2))
    id_facture = Column(String(10), ForeignKey("Facture.id_facture"))

# ============================================
# TABLE : PROJET
# ============================================

class Projet(Base):
    """ORM model for the 'Projet' table.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    __tablename__ = "Projet"
    id_projet = Column(String(10), primary_key=True)
    nom_projet = Column(String(100))
    statut = Column(String(50))
    date_debut = Column(Date)
    date_fin = Column(Date)
    montant_total_estime = Column(DECIMAL(12, 2))
    type_marche = Column(String(50))
    id_client = Column(String(10), ForeignKey("Client.id_client"))

# ============================================
# TABLE : GERER (LIEN RESPONSABLE / PROJET)
# ============================================

class Gerer(Base):
    """ORM model for the 'Gerer' association table.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    __tablename__ = "Gerer"
    id_personnel = Column(String(10), ForeignKey("ResponsableProjet.id_personnel"), primary_key=True)
    id_projet = Column(String(10), ForeignKey("Projet.id_projet"), primary_key=True)

# ============================================
# TABLE : TACHE
# ============================================

class Tache(Base):
    """ORM model for the 'Tache' table.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    __tablename__ = "Tache"
    id_tache = Column(String(10), primary_key=True)
    id_phase = Column(String(10), ForeignKey("Phase.id_phase"))
    nom_tache = Column(String(100))
    description = Column(Text)
    alerte_retard = Column(Boolean)
    conges_integres = Column(Boolean)
    statut = Column(Enum("à faire", "en cours", "terminé"))
    est_realisable = Column(Boolean)
    date_debut = Column(Date)
    date_fin = Column(Date)

# ============================================
# TABLE : PLANIFICATION COLLABORATEUR
# ============================================

class PlanificationCollaborateur(Base):
    """ORM model for the 'PlanificationCollaborateur' table.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    __tablename__ = "PlanificationCollaborateur"
    id_planification = Column(String(10), primary_key=True)
    id_tache = Column(String(10), ForeignKey("Tache.id_tache"))
    id_collaborateur = Column(String(10), ForeignKey("Collaborateur.id_personnel"))
    heures_disponibles = Column(DECIMAL(5, 2))
    alerte_depassement = Column(Boolean)
    semaine = Column(String(10))
    heures_prevues = Column(DECIMAL(5, 2))

# ============================================
# TABLE : PRESTATION COLLABORATEUR
# ============================================

class PrestationCollaborateur(Base):
    """ORM model for the 'PrestationCollaborateur' table.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    __tablename__ = "PrestationCollaborateur"
    id_prestation = Column(String(10), primary_key=True)
    date = Column(Date)
    id_tache = Column(String(10), ForeignKey("Tache.id_tache"))
    id_collaborateur = Column(String(10), ForeignKey("Collaborateur.id_personnel"))
    heures_effectuees = Column(DECIMAL(5, 2))
    mode_facturation = Column(Enum("horaire", "forfaitaire"))
    facture_associee = Column(String(10), ForeignKey("Facture.id_facture"))
    taux_horaire = Column(DECIMAL(8, 2))
    commentaire = Column(Text)

# ============================================
# TABLE : COUT
# ============================================

class Cout(Base):
    """ORM model for the 'Cout' table.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    __tablename__ = "Cout"
    id_cout = Column(String(10), primary_key=True)
    type_cout = Column(String(50))
    montant = Column(DECIMAL(10, 2))
    nature_cout = Column(Enum("interne", "externe", "logiciel", "matériel", "sous-traitant"))
    date = Column(Date)
    source = Column(String(50))

# ============================================
# TABLE : PROJECTION FACTURATION
# ============================================

class ProjectionFacturation(Base):
    """ORM model for the 'ProjectionFacturation' table.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.2 21/06/2025)
    """

    __tablename__ = "ProjectionFacturation"
    id_projection = Column(String(10), primary_key=True)
    mois = Column(String(7))
    montant_projete = Column(DECIMAL(10, 2))
    montant_facturable_actuel = Column(DECIMAL(10, 2))
    seuil_minimal = Column(DECIMAL(10, 2))
    alerte_facturation = Column(Boolean)
    id_projet = Column(String(10), ForeignKey("Projet.id_projet"))
    est_certain = Column(Boolean, default=True)

# ============================================
# TABLE : IMPORT LOG
# ============================================

class ImportLog(Base):
    """ORM model for the 'ImportLog' table.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.1 19/06/2025)
    """

    __tablename__ = "ImportLog"
    id_import = Column(String(10), primary_key=True)
    source = Column(String(100))
    type_donnee = Column(String(50))
    date_import = Column(Date)
    statut = Column(String(20))
    message_log = Column(Text)

# ============================================
# TABLE : HONORAIRE REPARTI
# ============================================

class HonoraireReparti(Base):
    """ORM model for the 'HonoraireReparti' table.
    Version:
    --------
    specification: Esteban Barracho (v.1 21/06/2025)
    implement: Esteban Barracho (v.1 21/06/2025)
    """

    __tablename__ = "HonoraireReparti"
    id_repartition = Column(String(10), primary_key=True)
    id_projet = Column(String(10), ForeignKey("Projet.id_projet"))
    societe = Column(String(100))
    montant = Column(DECIMAL(10, 2))
