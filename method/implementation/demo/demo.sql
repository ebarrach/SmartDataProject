-- 🔁 Nettoyage (optionnel pour éviter les conflits si déjà présent)
DELETE FROM HonoraireReparti WHERE id_projet = 'P003';
DELETE FROM ProjectionFacturation WHERE id_projection = 'PROJ003';
DELETE FROM PrestationCollaborateur WHERE id_prestation = 'PR003';
DELETE FROM PlanificationCollaborateur WHERE id_planification = 'PL003';
DELETE FROM Tache WHERE id_tache = 'T003';
DELETE FROM Phase WHERE id_phase = 'PH003';
DELETE FROM Facture WHERE id_facture = 'F003';
DELETE FROM Projet WHERE id_projet = 'P003';
DELETE FROM Client WHERE id_client = 'C003';

-- 1️⃣ Client : Vincent Pirnay
INSERT INTO Client (id_client, nom_client, adresse, secteur_activite)
VALUES ('C003', 'Vincent Pirnay', 'Rue de l''Industrie 45, 1000 Bruxelles', 'Énergie');

-- 2️⃣ Projet : Audit énergétique Bruxelles
INSERT INTO Projet (
    id_projet, nom_projet, statut, date_debut, date_fin,
    montant_total_estime, type_marche, id_client,
    type_projet, region, maitre_ouvrage, architecte, contact_client
) VALUES (
             'P003', 'Audit énergétique Bruxelles', 'en cours', '2025-06-01', '2025-09-30',
             25000.00, 'privé', 'C003',
             'PEB', 'Bruxelles', 'Vincent Pirnay', 'Arch. Dumont', 'vincent.pirnay@energy.be'
         );

-- 3️⃣ Facture liée au projet
INSERT INTO Facture (
    id_facture, date_emission, montant_facture,
    transmission_electronique, annexe, statut,
    reference_banque, fichier_facture
) VALUES (
             'F003', '2025-06-21', 8000.00,
             TRUE, 'PDF annexé', 'émise',
             'BE65001234567890', 'facture_f001.pdf'
         );

-- 4️⃣ Phase : Étude préliminaire
INSERT INTO Phase (id_phase, nom_phase, ordre_phase, montant_phase, id_facture)
VALUES ('PH003', 'Étude préliminaire', 1, 8000.00, 'F003');

-- 5️⃣ Vérification/ajout du collaborateur P001
INSERT INTO Collaborateur (id_personnel)
SELECT 'P001'
WHERE NOT EXISTS (
    SELECT 1 FROM Collaborateur WHERE id_personnel = 'P001'
);

-- 6️⃣ Tâche : Collecte de données
INSERT INTO Tache (
    id_tache, id_phase, nom_tache, description,
    alerte_retard, conges_integres, statut,
    est_realisable, date_debut, date_fin,
    heures_estimees, heures_prestées, heures_depassees
) VALUES (
             'T003', 'PH003', 'Collecte de données', 'Analyse des factures et relevés de consommation',
             FALSE, TRUE, 'en cours',
             TRUE, '2025-06-21', '2025-06-28',
             NULL, NULL, NULL
         );

-- 7️⃣ Planification du collaborateur P001
INSERT INTO PlanificationCollaborateur (
    id_planification, id_tache, id_collaborateur,
    heures_disponibles, alerte_depassement,
    semaine, heures_prevues
) VALUES (
             'PL003', 'T003', 'P001',
             8.0, FALSE,
             '2025-W26', 8.0
         );

-- 8️⃣ Prestation réelle
INSERT INTO PrestationCollaborateur (
    id_prestation, date, id_tache, id_collaborateur,
    heures_effectuees, mode_facturation,
    facture_associee, taux_horaire, commentaire
) VALUES (
             'PR003', '2025-06-21', 'T003', 'P001',
             7.5, 'horaire',
             'F003', 95.00, 'Début d''analyse des données collectées'
         );

-- 9️⃣ Projection de facturation
INSERT INTO ProjectionFacturation (
    id_projection, mois, montant_projete,
    montant_facturable_actuel, seuil_minimal,
    alerte_facturation, id_projet
) VALUES (
             'PROJ003', '2025-06', 8000.00,
             7200.00, 7000.00,
             FALSE, 'P003'
         );

-- 🔟 Indicateur d'incertitude sur la projection
UPDATE ProjectionFacturation
SET est_certain = FALSE
WHERE id_projection = 'PROJ003';

-- 🔁 Répartition des honoraires entre entités
INSERT INTO HonoraireReparti (id_repartition, id_projet, societe, montant)
VALUES
    ('HR001', 'P003', 'Pirnay SA', 15000.00),
    ('HR002', 'P003', 'Poly-Tech Engineering', 10000.00);
