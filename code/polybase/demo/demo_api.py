# ============================================
# SCRIPT: DEMO INTERACTIF POLYBASE - SQLAlchemy
# ============================================
# specification: Esteban Barracho (v.1 21/06/2025)
# implement: Esteban Barracho (v.4 22/06/2025)

import sys
import os
from sqlalchemy import create_engine, select, delete
from sqlalchemy.orm import Session
from datetime import date

# 📌 Ajout du chemin vers le dossier contenant `app/` pour les imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models import (
    Client, Projet, Facture, Phase, Tache,
    PlanificationCollaborateur, PrestationCollaborateur,
    ProjectionFacturation, Collaborateur, Cout
)

DATABASE_URL = "mysql+pymysql://root:polyroot@127.0.0.1:3307/PolyBase"
engine = create_engine(DATABASE_URL, echo=False)

# ============================================================
# Utilitaires
# ============================================================

def step(title):
    print(f"\n=== {title} ===")
    input("\u25B6\uFE0F Appuie sur [Entrée] pour continuer...\n")


def safe_delete(session, model, id_field, value):
    session.execute(delete(model).where(getattr(model, id_field) == value))


# ============================================================
# Exécution pas à pas
# ============================================================

with Session(engine) as session:
    # ⭮️ 0. Nettoyage préalable
    step("0. Suppression dynamique des anciennes entrées")
    safe_delete(session, ProjectionFacturation, "id_projection", "PROJ003")
    safe_delete(session, PrestationCollaborateur, "id_prestation", "PR003")
    safe_delete(session, PlanificationCollaborateur, "id_planification", "PL003")
    safe_delete(session, Tache, "id_tache", "T003")
    safe_delete(session, Phase, "id_phase", "PH003")
    safe_delete(session, Facture, "id_facture", "F003")
    safe_delete(session, Projet, "id_projet", "P003")
    safe_delete(session, Client, "id_client", "C003")
    safe_delete(session, Cout, "id_cout", "HR001")
    safe_delete(session, Cout, "id_cout", "HR002")
    session.commit()

    # ⭮️ 0. Vérification/création collaborateur
    step("0. Vérification ou création du collaborateur P001")
    if not session.get(Collaborateur, "P001"):
        session.add(Collaborateur(id_personnel="P001"))
        session.commit()

    # 1️⃣ Client
    step("1. Création du client Vincent Pirnay")
    session.add(Client(
        id_client="C003",
        nom_client="Vincent Pirnay",
        adresse="Rue de l'Industrie 45, 1000 Bruxelles",
        secteur_activite="Énergie"
    ))
    session.commit()

    # 2️⃣ Projet
    step("2. Création du projet lié à ce client")
    session.add(Projet(
        id_projet="P003",
        nom_projet="Audit énergétique Bruxelles",
        statut="en_cours",
        date_debut=date(2025, 6, 1),
        date_fin=date(2025, 9, 30),
        montant_total_estime=25000.00,
        type_marche="privé",
        id_client="C003"
    ))
    session.commit()

    # 3️⃣ Facture
    step("3. Facture liée au projet")
    session.add(Facture(
        id_facture="F003",
        date_emission=date(2025, 6, 21),
        montant_facture=8000.00,
        transmission_electronique=True,
        annexe="PDF annexé",
        statut="emise",
        reference_banque="BE65001234567890",
        fichier_facture="facture_f001.pdf"
    ))
    session.commit()

    # 4️⃣ Phase
    step("4. Phase du projet (étude préliminaire)")
    session.add(Phase(
        id_phase="PH003",
        nom_phase="Étude préliminaire",
        ordre_phase=1,
        montant_phase=8000.00,
        id_facture="F003"
    ))
    session.commit()

    # 5️⃣ Tâche
    step("5. Tâche à réaliser dans la phase")
    session.add(Tache(
        id_tache="T003",
        id_phase="PH003",
        nom_tache="Collecte de données",
        description="Analyse des factures et relevés de consommation",
        alerte_retard=False,
        conges_integres=True,
        statut="en_cours",
    est_realisable=True,
        date_debut=date(2025, 6, 21),
        date_fin=date(2025, 6, 28)
    ))
    session.commit()

    # 6️⃣ Planification
    step("6. Planification du collaborateur P001")
    session.add(PlanificationCollaborateur(
        id_planification="PL003",
        id_tache="T003",
        id_collaborateur="P001",
        heures_disponibles=8.0,
        alerte_depassement=False,
        semaine="2025-W26",
        heures_prevues=8.0
    ))
    session.commit()

    # 7️⃣ Prestation
    step("7. Enregistrement de la prestation réelle")
    session.add(PrestationCollaborateur(
        id_prestation="PR003",
        date=date(2025, 6, 21),
        id_tache="T003",
        id_collaborateur="P001",
        heures_effectuees=7.5,
        mode_facturation="horaire",
        facture_associee="F003",
        taux_horaire=95.00,
        commentaire="Début d'analyse des données collectées"
    ))
    session.commit()

    # 8️⃣ Projection de facturation
    step("8. Projection de facturation")
    session.add(ProjectionFacturation(
        id_projection="PROJ003",
        mois="2025-06",
        montant_projete=8000.00,
        montant_facturable_actuel=7200.00,
        seuil_minimal=7000.00,
        alerte_facturation=False,
        id_projet="P003"
    ))
    session.commit()

    # 9️⃣ Mise à jour : est_certain = False
    step("9. Mise à jour de l'indicateur d'incertitude")
    projection = session.get(ProjectionFacturation, "PROJ003")
    if projection:
        projection.est_certain = False
    session.commit()

    # 🔟 Répartition des honoraires
    step("10. Répartition des honoraires entre entités")
    session.add_all([
        Cout(id_cout="HR001", type_cout="honoraire", montant=15000.00, nature_cout="externe", date=date.today(),
             source="Pirnay SA", id_projet="P003"),
        Cout(id_cout="HR002", type_cout="honoraire", montant=10000.00, nature_cout="interne", date=date.today(),
             source="Poly-Tech Engineering", id_projet="P003")
    ])
    session.commit()

    print("\n🎉 Démonstration complète avec SQLAlchemy terminée.")
