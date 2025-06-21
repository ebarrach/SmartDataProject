-- *********************************************
-- * Standard SQL generation corrigée
-- *--------------------------------------------
-- * DB-MAIN version: 11.0.2
-- * Generator date: Juin 2025
-- * Modifié par Esteban BARRACHO
-- *********************************************

-- DROP DATABASE PolyBase;
-- CREATE DATABASE PolyBase;
drop schema if exists Polybase;
create schema Polybase;
USE Polybase;

-- Tables Section
-- _______________

-- TABLE DES RESPONSABLES DE PROJET
create table ResponsableProjet (
                                   id_personnel varchar(10) not null,
                                   niveau_hierarchique varchar(50) not null,
                                   constraint FKPer_Res_ID primary key (id_personnel)
);

-- TABLE DES CLIENTS
create table Client (
                        id_client varchar(10) not null,
                        nom_client varchar(100) not null,
                        adresse TEXT not null,
                        secteur_activite varchar(100) not null,
                        constraint ID_Client_ID primary key (id_client)
);

-- TABLE DU PERSONNEL
create table Personnel (
                           id_personnel varchar(10) not null,
                           type_personnel ENUM('interne', 'externe') not null,
                           nom varchar(100) not null,
                           prenom varchar(100) not null,
                           email varchar(100) not null,
                           fonction varchar(100) not null,
                           taux_honoraire_standard decimal(8,2) not null,
                           constraint ID_Personnel_ID primary key (id_personnel)
);

-- TABLE DES COLLABORATEURS (SPÉCIALISATION DU PERSONNEL)
create table Collaborateur (
                               id_personnel varchar(10) not null,
                               constraint PK_Collaborateur primary key (id_personnel),
                               constraint FKPer_Col_FK foreign key (id_personnel) references Personnel(id_personnel)
);

-- TABLE DES FACTURES (créée avant Phase pour éviter erreur de FK)
create table Facture (
                         id_facture varchar(10) not null,
                         date_emission date not null,
                         montant_facture decimal(10,2) not null,
                         transmission_electronique boolean not null,
                         annexe TEXT not null,
                         statut ENUM('émise', 'payée', 'en attente') not null,
                         reference_banque varchar(100) not null,
                         fichier_facture TEXT not null,
                         constraint ID_Facture_ID primary key (id_facture)
);

-- TABLE DES PHASES DE PROJET
create table Phase (
                       id_phase varchar(10) not null,
                       nom_phase varchar(100) not null,
                       ordre_phase INT not null,
                       montant_phase decimal(10,2) not null,
                       id_facture varchar(10),
                       constraint ID_Phase_ID primary key (id_phase),
                       foreign key (id_facture) references Facture(id_facture)
);

-- TABLE DES PROJETS
create table Projet (
                        id_projet varchar(10) not null,
                        nom_projet varchar(100) not null,
                        statut varchar(50) not null,
                        date_debut date not null,
                        date_fin date not null,
                        montant_total_estime decimal(12,2) not null,
                        type_marche varchar(50) not null,
                        id_client varchar(10) not null,
                        constraint ID_Projet_ID primary key (id_projet),
                        foreign key (id_client) references Client(id_client)
);

ALTER TABLE Projet
    ADD COLUMN type_projet VARCHAR(50) NULL,
    ADD COLUMN region VARCHAR(50) NULL,
    ADD COLUMN maitre_ouvrage VARCHAR(100) NULL,
    ADD COLUMN architecte VARCHAR(100) NULL,
    ADD COLUMN contact_client VARCHAR(100) NULL;

-- TABLE REPARTITION DES HONORAIRE

CREATE TABLE HonoraireReparti (
                                  id_repartition VARCHAR(10) PRIMARY KEY,
                                  id_projet VARCHAR(10) NOT NULL,
                                  societe VARCHAR(50) NOT NULL, -- 'Poly-Tech', 'Pirnay', etc.
                                  montant DECIMAL(10,2) NOT NULL,
                                  FOREIGN KEY (id_projet) REFERENCES Projet(id_projet)
);


-- TABLE ASSOCIATIVE GERER (ResponsableProjet ↔ Projet)
create table Gerer (
                       id_projet varchar(10) not null,
                       id_personnel varchar(10) not null,
                       constraint ID_Gerer_ID primary key (id_personnel, id_projet),
                       foreign key (id_personnel) references ResponsableProjet(id_personnel),
                       foreign key (id_projet) references Projet(id_projet)
);

-- TABLE DES TÂCHES
create table Tache (
                       id_tache varchar(10) not null,
                       id_phase varchar(10) not null,
                       nom_tache varchar(100) not null,
                       description TEXT not null,
                       alerte_retard boolean not null,
                       conges_integres boolean not null,
                       statut ENUM('à faire', 'en cours', 'terminé') not null,
                       est_realisable boolean not null,
                       date_debut date not null,
                       date_fin date not null,
                       heures_estimees DECIMAL(5,2),
                       heures_prestées DECIMAL(5,2),
                       heures_depassees DECIMAL(5,2),
                       constraint ID_Tache_ID primary key (id_tache),
                       foreign key (id_phase) references Phase(id_phase)
);



-- TABLE DE PLANIFICATION DES COLLABORATEURS
create table PlanificationCollaborateur (
                                            id_planification varchar(10) not null,
                                            id_tache varchar(10) not null,
                                            id_collaborateur varchar(10) not null,
                                            heures_disponibles decimal(5,2) not null,
                                            alerte_depassement boolean not null,
                                            semaine varchar(10) not null,
                                            heures_prevues decimal(5,2) not null,
                                            constraint ID_PlanificationCollaborateur_ID primary key (id_planification),
                                            foreign key (id_tache) references Tache(id_tache),
                                            foreign key (id_collaborateur) references Collaborateur(id_personnel)
);

-- TABLE DES PRESTATIONS DES COLLABORATEURS
create table PrestationCollaborateur (
                                         id_prestation varchar(10) not null,
                                         date date not null,
                                         id_tache varchar(10) not null,
                                         id_collaborateur varchar(10) not null,
                                         heures_effectuees decimal(5,2) not null,
                                         mode_facturation ENUM('horaire', 'forfaitaire') not null,
                                         facture_associee varchar(10),
                                         taux_horaire decimal(8,2) not null,
                                         commentaire TEXT not null,
                                         constraint ID_PrestationCollaborateur_ID primary key (id_prestation),
                                         foreign key (id_tache) references Tache(id_tache),
                                         foreign key (id_collaborateur) references Collaborateur(id_personnel),
                                         foreign key (facture_associee) references Facture(id_facture)
);

-- TABLE DES COÛTS
create table Cout (
                      id_cout varchar(10) not null,
                      type_cout varchar(50) not null,
                      montant decimal(10,2) not null,
                      nature_cout ENUM('interne', 'externe', 'logiciel', 'matériel', 'sous-traitant') not null,
                      date date not null,
                      source varchar(50) not null,
                      constraint ID_Cout_ID primary key (id_cout)
);

-- TABLE DES PROJECTIONS DE FACTURATION
create table ProjectionFacturation (
                                       id_projection varchar(10) not null,
                                       mois varchar(7) not null,
                                       montant_projete decimal(10,2) not null,
                                       montant_facturable_actuel decimal(10,2) not null,
                                       seuil_minimal decimal(10,2) not null,
                                       alerte_facturation boolean not null,
                                       id_projet varchar(10) not null,
                                       constraint ID_ProjectionFacturation_ID primary key (id_projection),
                                       foreign key (id_projet) references Projet(id_projet)
);

ALTER TABLE ProjectionFacturation
    ADD COLUMN est_certain BOOLEAN DEFAULT TRUE;


-- TABLE DES LOGS D'IMPORT
create table ImportLog (
                           id_import varchar(10) not null,
                           source varchar(100) not null,
                           type_donnee varchar(50) not null,
                           date_import date not null,
                           statut varchar(20) not null,
                           message_log TEXT not null,
                           constraint ID_ImportLog_ID primary key (id_import)
);

-- ======= CLIENTS =======
INSERT INTO Client (id_client, nom_client, adresse, secteur_activite)
VALUES
    ('CL001', 'Poly-Tech Engineering', 'Rue des Sciences 10, 5000 Namur', 'Ingénierie'),
    ('CL002', 'GreenSys Solutions', 'Chaussée Verte 45, 1300 Wavre', 'Énergies renouvelables');

-- ======= PERSONNEL =======
INSERT INTO Personnel (id_personnel, type_personnel, nom, prenom, email, fonction, taux_honoraire_standard)
VALUES
    ('P001', 'interne', 'Durand', 'Alice', 'alice.durand@polytech.be', 'Chef de projet', 95.00),
    ('P002', 'externe', 'Leclercq', 'Marc', 'marc.leclercq@freelance.be', 'Consultant IT', 120.00);

-- ======= RESPONSABLES PROJET =======
INSERT INTO ResponsableProjet (id_personnel, niveau_hierarchique)
VALUES
    ('P001', 'Senior Manager');

-- ======= COLLABORATEURS =======
INSERT INTO Collaborateur (id_personnel)
VALUES
    ('P002');

-- ======= FACTURES =======
INSERT INTO Facture (id_facture, date_emission, montant_facture, transmission_electronique, annexe, statut, reference_banque, fichier_facture)
VALUES
    ('F001', '2025-06-01', 15000.00, TRUE, 'PDF annexé', 'émise', 'BE34001234567890', 'facture_f001.pdf');

-- ======= PROJETS =======
INSERT INTO Projet (id_projet, nom_projet, statut, date_debut, date_fin, montant_total_estime, type_marche, id_client)
VALUES
    ('PRJ001', 'Migration Système ERP', 'en cours', '2025-06-01', '2025-12-31', 25000.00, 'public', 'CL001');

-- ======= GERER (association) =======
INSERT INTO Gerer (id_personnel, id_projet)
VALUES
    ('P001', 'PRJ001');

-- ======= PHASE =======
INSERT INTO Phase (id_phase, nom_phase, ordre_phase, montant_phase, id_facture)
VALUES
    ('PH001', 'Analyse', 1, 10000.00, 'F001');

-- ======= TACHES =======
INSERT INTO Tache (
    id_tache, id_phase, nom_tache, description, alerte_retard, conges_integres,
    statut, est_realisable, date_debut, date_fin, heures_estimees, heures_prestées, heures_depassees
) VALUES (
             'T001', 'PH001', 'Audit existant', 'Évaluation du système actuel',
             FALSE, TRUE, 'en cours',
             TRUE, '2025-06-01', '2025-06-10',
             35.00, 37.50, 2.50
         );

-- ======= PLANIFICATION COLLABORATEUR =======
INSERT INTO PlanificationCollaborateur (id_planification, id_tache, id_collaborateur, heures_disponibles, alerte_depassement, semaine, heures_prevues)
VALUES
    ('PL001', 'T001', 'P002', 40.00, FALSE, '2025-W23', 35.00);

-- ======= PRESTATION COLLABORATEUR =======
INSERT INTO PrestationCollaborateur (
    id_prestation, date, id_tache, id_collaborateur, heures_effectuees, mode_facturation,
    facture_associee, taux_horaire, commentaire
) VALUES (
             'PC001', '2025-06-21', 'T001',
             'P002', 37.50, 'horaire',
             'F001', 120.00, 'Phase d’audit réalisée selon planning.'
         );

-- ======= COUTS =======
INSERT INTO Cout (id_cout, type_cout, montant, nature_cout, date, source)
VALUES
    ('C001', 'Location serveur', 500.00, 'interne', '2025-06-01', 'DataCenter Local');

-- ======= PROJECTION FACTURATION =======
INSERT INTO ProjectionFacturation (id_projection, mois, montant_projete, montant_facturable_actuel, seuil_minimal, alerte_facturation, id_projet)
VALUES
    ('PF001', '2025-06', 20000.00, 15000.00, 18000.00, FALSE, 'PRJ001');

-- ======= IMPORT LOGS =======
INSERT INTO ImportLog (id_import, source, type_donnee, date_import, statut, message_log)
VALUES
    ('IMP001', 'Excel v2025', 'Personnel', '2025-06-01', 'succès', 'Import initial sans erreurs.');

-- ======= VUE =======
CREATE VIEW VueAnalyseTache AS
SELECT
    T.id_tache,
    T.nom_tache,
    SUM(P.heures_effectuees) AS heures_prestées,
    PC.heures_prevues AS heures_estimees,
    GREATEST(SUM(P.heures_effectuees) - PC.heures_prevues, 0) AS heures_depassees
FROM Tache T
         JOIN PlanificationCollaborateur PC ON PC.id_tache = T.id_tache
         LEFT JOIN PrestationCollaborateur P ON P.id_tache = T.id_tache
GROUP BY T.id_tache, T.nom_tache, PC.heures_prevues;

CREATE VIEW VuePrestationsNonFacturees AS
SELECT
    PC.id_prestation,
    PC.id_tache,
    PC.id_collaborateur,
    PC.date,
    PC.heures_effectuees,
    PC.taux_horaire,
    (PC.heures_effectuees * PC.taux_horaire) AS montant_encours
FROM PrestationCollaborateur PC
WHERE PC.facture_associee IS NULL;


-- ======= TRIGGER =======
-- 🔁 Nettoyage préalable
DROP TRIGGER IF EXISTS maj_heures_tache;
DROP TRIGGER IF EXISTS maj_depassement_apres_modif_estimee;
DROP TRIGGER IF EXISTS maj_heures_apres_modif_prestation;
DROP TRIGGER IF EXISTS maj_alerte_retard;

DELIMITER $$

-- 🎯 Trigger 1 : mise à jour des heures après INSERT d'une prestation
CREATE TRIGGER maj_heures_tache
    AFTER INSERT ON PrestationCollaborateur
    FOR EACH ROW
BEGIN
    DECLARE total_heures DECIMAL(5,2);
    DECLARE heures_estimees DECIMAL(5,2);
    DECLARE depassement DECIMAL(5,2);

    SELECT COALESCE(SUM(heures_effectuees), 0)
    INTO total_heures
    FROM PrestationCollaborateur
    WHERE id_tache = NEW.id_tache;

    SELECT heures_estimees
    INTO heures_estimees
    FROM Tache
    WHERE id_tache = NEW.id_tache;

    SET depassement = GREATEST(total_heures - heures_estimees, 0);

    UPDATE Tache
    SET heures_prestées = total_heures,
        heures_depassees = depassement
    WHERE id_tache = NEW.id_tache;
END$$

-- 🎯 Trigger 2 : mise à jour du dépassement si heures estimées ou prestées changent
CREATE TRIGGER maj_depassement_apres_modif_tache
    BEFORE UPDATE ON Tache
    FOR EACH ROW
BEGIN
    DECLARE depassement DECIMAL(5,2);

    IF NEW.heures_estimees != OLD.heures_estimees OR NEW.heures_prestées != OLD.heures_prestées THEN
        SET depassement = GREATEST(NEW.heures_prestées - NEW.heures_estimees, 0);
        SET NEW.heures_depassees = depassement;
    END IF;
END$$

-- 🎯 Trigger 3 : mise à jour des heures après modification d'une prestation
CREATE TRIGGER maj_heures_apres_modif_prestation
    AFTER UPDATE ON PrestationCollaborateur
    FOR EACH ROW
BEGIN
    DECLARE total_heures DECIMAL(5,2);
    DECLARE heures_estimees DECIMAL(5,2);
    DECLARE depassement DECIMAL(5,2);

    IF NEW.heures_effectuees != OLD.heures_effectuees THEN
        SELECT COALESCE(SUM(heures_effectuees), 0)
        INTO total_heures
        FROM PrestationCollaborateur
        WHERE id_tache = NEW.id_tache;

        SELECT heures_estimees
        INTO heures_estimees
        FROM Tache
        WHERE id_tache = NEW.id_tache;

        SET depassement = GREATEST(total_heures - heures_estimees, 0);

        UPDATE Tache
        SET heures_prestées = total_heures,
            heures_depassees = depassement
        WHERE id_tache = NEW.id_tache;
    END IF;
END$$

-- 🎯 Trigger 4 : alerte de retard automatique
CREATE TRIGGER maj_alerte_retard
    BEFORE UPDATE ON Tache
    FOR EACH ROW
BEGIN
    IF CURDATE() > NEW.date_fin AND NEW.statut != 'terminé' THEN
        SET NEW.alerte_retard = TRUE;
    ELSE
        SET NEW.alerte_retard = FALSE;
    END IF;
END$$

DELIMITER ;





