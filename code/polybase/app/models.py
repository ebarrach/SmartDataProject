# ============================================
# IMPORTS
# ============================================

from sqlalchemy import Column, String, Enum, Date, Boolean, DECIMAL, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from .database import Base

# ============================================
# TABLE : PERSONNEL
# ============================================

class Personnel(Base):
    """ORM model for the 'Personnel' table.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.2 22/06/2025)
    """
    __tablename__ = "Personnel"
    id_personnel = Column(String(10), primary_key=True, index=True)
    type_personnel = Column(Enum("interne", "externe"))
    nom = Column(String(100))
    prenom = Column(String(100))
    email = Column(String(100))
    password = Column(String(255))
    fonction = Column(String(100))
    taux_honoraire_standard = Column(DECIMAL(8, 2))

    collaborateur = relationship("Collaborateur", back_populates="personnel", uselist=False)
    responsable = relationship("ResponsableProjet", back_populates="personnel", uselist=False)
    assert __tablename__ == "Personnel"

# ============================================
# TABLE : RESPONSABLE PROJET
# ============================================

class ResponsableProjet(Base):
    """ORM model for the 'ResponsableProjet' table.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.2 22/06/2025)
    """
    __tablename__ = "ResponsableProjet"
    id_personnel = Column(String(10), ForeignKey("Personnel.id_personnel"), primary_key=True)
    niveau_hierarchique = Column(String(50))

    personnel = relationship("Personnel", back_populates="responsable")
    projets = relationship("Gerer", back_populates="responsable")
    assert __tablename__ == "ResponsableProjet"

# ============================================
# TABLE : CLIENT
# ============================================

class Client(Base):
    """ORM model for the 'Client' table.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.2 22/06/2025)
    """
    __tablename__ = "Client"
    id_client = Column(String(10), primary_key=True)
    nom_client = Column(String(100))
    adresse = Column(Text)
    secteur_activite = Column(String(100))

    projets = relationship("Projet", back_populates="client")
    assert __tablename__ == "Client"

# ============================================
# TABLE : COLLABORATEUR
# ============================================

class Collaborateur(Base):
    """ORM model for the 'Collaborateur' table.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.2 22/06/2025)
    """
    __tablename__ = "Collaborateur"
    id_personnel = Column(String(10), ForeignKey("Personnel.id_personnel"), primary_key=True)

    personnel = relationship("Personnel", back_populates="collaborateur")
    planifications = relationship("PlanificationCollaborateur", back_populates="collaborateur")
    prestations = relationship("PrestationCollaborateur", back_populates="collaborateur")
    assert __tablename__ == "Collaborateur"

# ============================================
# TABLE : FACTURE
# ============================================

class Facture(Base):
    """ORM model for the 'Facture' table.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.2 22/06/2025)
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

    phases = relationship("Phase", back_populates="facture")
    prestations = relationship("PrestationCollaborateur", back_populates="facture")
    assert __tablename__ == "Facture"

# ============================================
# TABLE : PHASE
# ============================================

class Phase(Base):
    """ORM model for the 'Phase' table.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.2 22/06/2025)
    """
    __tablename__ = "Phase"
    id_phase = Column(String(10), primary_key=True)
    nom_phase = Column(String(100))
    ordre_phase = Column(Integer)
    montant_phase = Column(DECIMAL(10, 2))
    id_facture = Column(String(10), ForeignKey("Facture.id_facture"))

    facture = relationship("Facture", back_populates="phases")
    taches = relationship("Tache", back_populates="phase")
    assert __tablename__ == "Phase"

# ============================================
# TABLE : PROJET
# ============================================

class Projet(Base):
    """ORM model for the 'Projet' table.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.2 22/06/2025)
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

    client = relationship("Client", back_populates="projets")
    projections = relationship("ProjectionFacturation", back_populates="projet")
    honoraires = relationship("HonoraireReparti", back_populates="projet")
    assert __tablename__ == "Projet"

# ============================================
# TABLE : GERER (LIEN RESPONSABLE / PROJET)
# ============================================

class Gerer(Base):
    """ORM model for the 'Gerer' association table.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.2 22/06/2025)
    """
    __tablename__ = "Gerer"
    id_personnel = Column(String(10), ForeignKey("ResponsableProjet.id_personnel"), primary_key=True)
    id_projet = Column(String(10), ForeignKey("Projet.id_projet"), primary_key=True)

    responsable = relationship("ResponsableProjet", back_populates="projets")
    projet = relationship("Projet")
    assert __tablename__ == "Gerer"

# ============================================
# TABLE : TACHE
# ============================================

class Tache(Base):
    """ORM model for the 'Tache' table.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.3 23/06/2025)
    """
    __tablename__ = "Tache"
    id_tache = Column(String(10), primary_key=True)
    id_phase = Column(String(10), ForeignKey("Phase.id_phase"))
    nom_tache = Column(String(100))
    description = Column(Text)
    alerte_retard = Column(Boolean)
    conges_integres = Column(Boolean)
    statut = Column(Enum("a_faire", "en_cours", "termine"))
    est_realisable = Column(Boolean)
    date_debut = Column(Date)
    date_fin = Column(Date)
    heures_depassees = Column(DECIMAL(5, 2))

    phase = relationship("Phase", back_populates="taches")
    planifications = relationship("PlanificationCollaborateur", back_populates="tache")
    prestations = relationship("PrestationCollaborateur", back_populates="tache")
    assert __tablename__ == "Tache"

# ============================================
# TABLE : PLANIFICATION COLLABORATEUR
# ============================================

class PlanificationCollaborateur(Base):
    """ORM model for the 'PlanificationCollaborateur' table.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.2 22/06/2025)
    """
    __tablename__ = "PlanificationCollaborateur"
    id_planification = Column(String(10), primary_key=True)
    id_tache = Column(String(10), ForeignKey("Tache.id_tache"))
    id_collaborateur = Column(String(10), ForeignKey("Collaborateur.id_personnel"))
    heures_disponibles = Column(DECIMAL(5, 2))
    alerte_depassement = Column(Boolean)
    semaine = Column(String(10))
    heures_prevues = Column(DECIMAL(5, 2))

    tache = relationship("Tache", back_populates="planifications")
    collaborateur = relationship("Collaborateur", back_populates="planifications")
    assert __tablename__ == "PlanificationCollaborateur"

# ============================================
# TABLE : PRESTATION COLLABORATEUR
# ============================================

class PrestationCollaborateur(Base):
    """ORM model for the 'PrestationCollaborateur' table.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.2 22/06/2025)
    """
    __tablename__ = "PrestationCollaborateur"
    id_prestation = Column(String(10), primary_key=True)
    date = Column(Date)
    id_tache = Column(String(10), ForeignKey("Tache.id_tache"), nullable=True)
    id_projet = Column(String(10), ForeignKey("Projet.id_projet"), nullable=True)
    id_collaborateur = Column(String(10), ForeignKey("Collaborateur.id_personnel"))
    heures_effectuees = Column(DECIMAL(5, 2))
    mode_facturation = Column(Enum("horaire", "forfaitaire"))
    facture_associee = Column(String(10), ForeignKey("Facture.id_facture"))
    taux_horaire = Column(DECIMAL(8, 2))
    commentaire = Column(Text)

    tache = relationship("Tache", back_populates="prestations")
    collaborateur = relationship("Collaborateur", back_populates="prestations")
    facture = relationship("Facture", back_populates="prestations")
    projet = relationship("Projet")
    assert __tablename__ == "PrestationCollaborateur"

# ============================================
# TABLE : COUT
# ============================================

class Cout(Base):
    """ORM model for the 'Cout' table.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.2 26/06/2025)
    """
    __tablename__ = "Cout"
    id_cout = Column(String(10), primary_key=True)
    type_cout = Column(String(50))
    montant = Column(DECIMAL(10, 2))
    nature_cout = Column(Enum("interne", "externe", "logiciel", "matériel", "sous-traitant"))
    date = Column(Date)
    source = Column(String(50))
    id_projet = Column(String(10), ForeignKey("Projet.id_projet"), nullable=True)
    projet = relationship("Projet")
    assert __tablename__ == "Cout"

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

    projet = relationship("Projet", back_populates="projections")
    assert __tablename__ == "ProjectionFacturation"

# ============================================
# TABLE : IMPORT LOG
# ============================================

class ImportLog(Base):
    """ORM model for the 'ImportLog' table.
    Version:
    --------
    specification: Esteban Barracho (v.1 19/06/2025)
    implement: Esteban Barracho (v.2 26/06/2025)
    """
    __tablename__ = "ImportLog"
    id_import = Column(String(10), primary_key=True)
    source = Column(String(100))
    type_donnee = Column(String(50))
    date_import = Column(Date)
    statut = Column(String(20))
    message_log = Column(Text)
    id_projet = Column(String(10), ForeignKey("Projet.id_projet"), nullable=True)
    projet = relationship("Projet")
    assert __tablename__ == "ImportLog"

# ============================================
# TABLE : HONORAIRE REPARTI
# ============================================

class HonoraireReparti(Base):
    """ORM model for the 'HonoraireReparti' table.
    Version:
    --------
    specification: Esteban Barracho (v.1 21/06/2025)
    implement: Esteban Barracho (v.2 22/06/2025)
    """
    __tablename__ = "HonoraireReparti"
    id_repartition = Column(String(10), primary_key=True)
    id_projet = Column(String(10), ForeignKey("Projet.id_projet"))
    societe = Column(String(100))
    montant = Column(DECIMAL(10, 2))

    projet = relationship("Projet", back_populates="honoraires")
    assert __tablename__ == "HonoraireReparti"

# ============================================
# TABLE : OFFRE
# ============================================

class Offre(Base):
    """ORM model for the 'Offre' table.
    Version:
    --------
    specification: Esteban Barracho (v.1 24/06/2025)
    implement: Esteban Barracho (v.2 26/06/2025)
    """
    __tablename__ = "Offre"
    id_offre = Column(String(16), primary_key=True)
    annee = Column(Integer, nullable=False)
    entite = Column(String(16), nullable=False)
    type_marche = Column(String(16), nullable=False)
    nombre = Column(Integer, nullable=False)
    indicateur = Column(String(32))
    id_client = Column(String(10), ForeignKey("Client.id_client"), nullable=True)
    client = relationship("Client")
    assert __tablename__ == "Offre"

