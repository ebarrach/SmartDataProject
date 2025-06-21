"""
Script interactif de démonstration API PolyBase
Nettoyage + enregistrement + vérification pas à pas
"""

import httpx

BASE_URL = "http://localhost:8000"

def step(title):
    print(f"\n=== {title} ===")
    input("▶️ Appuie sur [Entrée] pour continuer...\n")

def post(endpoint, data):
    try:
        r = httpx.post(f"{BASE_URL}{endpoint}", json=data)
        print(f"[POST] {endpoint} -> {r.status_code}")
        try:
            print(r.json())
        except Exception:
            print("⚠️ Réponse brute (non-JSON) :", r.text)
    except Exception as e:
        print("❌ Exception HTTP:", e)

def delete(endpoint):
    try:
        r = httpx.delete(f"{BASE_URL}{endpoint}")
        print(f"[DELETE] {endpoint} -> {r.status_code}")
        if r.status_code != 200:
            print("⚠️", r.text)
    except Exception as e:
        print("❌ Exception HTTP:", e)

def get(endpoint):
    try:
        r = httpx.get(f"{BASE_URL}{endpoint}")
        print(f"[GET] {endpoint} -> {r.status_code}")
        try:
            print(r.json())
        except Exception:
            print("⚠️ Réponse brute (non-JSON) :", r.text)
    except Exception as e:
        print("❌ Exception HTTP:", e)

# 🔁 Étape 0 : Nettoyage dynamique des données précédentes
step("0. Suppression dynamique des anciennes entrées")
delete("/projection_facturation/PROJ003")
delete("/prestation/PR003")
delete("/planifications/PL003")
delete("/tasks/T003")
delete("/phases/PH003")
delete("/factures/F003")
delete("/projects/P003")
delete("/clients/C003")

# 🔁 Étape préliminaire : Assurer l'existence du collaborateur P001
step("0. Vérification ou création du collaborateur P001")
post("/collaborateurs", {
    "id_personnel": "P001"
})

# 1️⃣ Client
step("1. Création du client Vincent Pirnay")
post("/clients", {
    "id_client": "C003",
    "nom_client": "Vincent Pirnay",
    "adresse": "Rue de l'Industrie 45, 1000 Bruxelles",
    "secteur_activite": "Énergie"
})

# 2️⃣ Projet
step("2. Création du projet lié à ce client")
post("/projects", {
    "id_projet": "P003",
    "nom_projet": "Audit énergétique Bruxelles",
    "statut": "en cours",
    "date_debut": "2025-06-01",
    "date_fin": "2025-09-30",
    "montant_total_estime": 25000.00,
    "type_marche": "privé",
    "id_client": "C003"
})

# 3️⃣ Facture
step("3. Facture liée au projet")
post("/factures", {
    "id_facture": "F003",
    "date_emission": "2025-06-21",
    "montant_facture": 8000.00,
    "transmission_electronique": True,
    "annexe": "PDF annexé",
    "statut": "émise",
    "reference_banque": "BE65001234567890",
    "fichier_facture": "facture_f001.pdf"
})

# 4️⃣ Phase
step("4. Phase du projet (étude préliminaire)")
post("/phases", {
    "id_phase": "PH003",
    "nom_phase": "Étude préliminaire",
    "ordre_phase": 1,
    "montant_phase": 8000.00,
    "id_facture": "F003"
})

# 5️⃣ Tâche
step("5. Tâche à réaliser dans la phase")
post("/tasks", {
    "id_tache": "T003",
    "id_phase": "PH003",
    "nom_tache": "Collecte de données",
    "description": "Analyse des factures et relevés de consommation",
    "alerte_retard": False,
    "conges_integres": True,
    "statut": "en cours",
    "est_realisable": True,
    "date_debut": "2025-06-21",
    "date_fin": "2025-06-28"
})

# 6️⃣ Planification
step("6. Planification du collaborateur P001")
post("/planifications", {
    "id_planification": "PL003",
    "id_tache": "T003",
    "id_collaborateur": "P001",
    "heures_disponibles": 8.0,
    "alerte_depassement": False,
    "semaine": "2025-W26",
    "heures_prevues": 8.0
})

# 7️⃣ Prestation
step("7. Enregistrement de la prestation réelle")
post("/prestation", {
    "id_prestation": "PR003",
    "date": "2025-06-21",
    "id_tache": "T003",
    "id_collaborateur": "P001",
    "heures_effectuees": 7.5,
    "mode_facturation": "horaire",
    "facture_associee": "F003",
    "taux_horaire": 95.00,
    "commentaire": "Début d'analyse des données collectées"
})

# 8️⃣ Projection
step("8. Projection de facturation")
post("/projection_facturation", {
    "id_projection": "PROJ003",
    "mois": "2025-06",
    "montant_projete": 8000.00,
    "montant_facturable_actuel": 7200.00,
    "seuil_minimal": 7000.00,
    "alerte_facturation": False,
    "id_projet": "P003"
})

# 9️⃣ Vue alertes
step("9. Affichage des alertes sur les tâches")
get("/dashboard/tasks/alertes")

# 🔟 Vue facturation
step("10. Vue facturation dans le dashboard")
get("/dashboard/facturation")

# 1️⃣1️⃣ Total heures dépassées
step("11. Total heures dépassées")
get("/dashboard/heures-depassees")

# 12️⃣ Multiplicating Factor
step("12. Calcul Multiplicating Factor")
get("/multiplicating-factor/8000/7200")
