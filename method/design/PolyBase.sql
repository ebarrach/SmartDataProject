-- *********************************************
-- * Standard SQL generation                   
-- *--------------------------------------------
-- * DB-MAIN version: 11.0.2              
-- * Generator date: Sep 14 2021              
-- * Generation date: Fri Jun 13 20:08:19 2025 
-- * LUN file: C:\Users\Esteban BARRACHO\Desktop\PolyBase\method\design\PolyBase.lun 
-- * Schema: Relation/SQL 
-- ********************************************* 


-- Database Section
-- ________________ 

create database Relation;


-- DBSpace Section
-- _______________


-- Tables Section
-- _____________ 

create table Facture (
     ID_Fac -- Sequence attribute not implemented -- not null,
     id_facture char(1) not null,
     date_emission char(1) not null,
     montant_facture char(1) not null,
     statut char(1) not null,
     reference_banque char(1) not null,
     fichier_facture char(1) not null,
     constraint ID_ID primary key (ID_Fac));

create table Cout (
     id_cout char(1) not null,
     type_cout char(1) not null,
     montant char(1) not null,
     date char(1) not null,
     source char(1) not null,
     constraint ID_Cout_ID primary key (id_cout));

create table ImportLog (
     id_import char(1) not null,
     source char(1) not null,
     type_donnee char(1) not null,
     date_import char(1) not null,
     statut char(1) not null,
     message_log char(1) not null,
     constraint ID_ImportLog_ID primary key (id_import));

create table Collaborateur (
     id_tache -- Compound attribute -- not null,
     id_personnel char(1) not null,
     constraint FKResponsable_ID primary key (id_tache -- Compound attribute --),
     constraint FKPer_Col_ID unique (id_personnel));

create table Comptable (
     id_personnel char(1) not null,
     accredidation_comptable char(1) not null,
     constraint FKPer_Com_ID primary key (id_personnel));

create table ChefProjet (
     id_personnel char(1) not null,
     niveau_hierarchique char(1) not null,
     constraint FKPer_Che_ID primary key (id_personnel));

create table Planification (
     id_planification char(1) not null,
     id_tache char(1) not null,
     id_collaborateur char(1) not null,
     semaine char(1) not null,
     heures_prevues char(1) not null,
     constraint ID_Planification_ID primary key (id_planification));

create table Prestation (
     id_prestation char(1) not null,
     date char(1) not null,
     id_tache char(1) not null,
     id_collaborateur char(1) not null,
     heures_effectuees char(1) not null,
     taux_horaire char(1) not null,
     commentaire char(1) not null,
     constraint ID_Prestation_ID primary key (id_prestation));

create table Phase (
     id_phase char(1) not null,
     nom_phase char(1) not null,
     ordre_phase char(1) not null,
     montant_phase char(1) not null,
     ID_Fac numeric(10),
     constraint ID_Phase_ID primary key (id_phase));

create table Tache (
     id_tache -- Compound attribute -- not null,
     id_phase char(1) not null,
     nom_tache char(1) not null,
     description char(1) not null,
     statut char(1) not null,
     date_debut char(1) not null,
     date_fin char(1) not null,
     constraint ID_Tache_ID primary key (id_tache -- Compound attribute --),
     constraint FKInclure_ID unique (id_phase));

create table Personnel (
     id_personnel varchar(10) not null,
     nom varchar(100) not null,
     prenom varchar(100) not null,
     email varchar(100) not null,
     fonction varchar(50) not null,
     taux_honoraire_standard decimal(10,2) not null,
     Comptable char(1),
     Collaborateur char(1),
     ChefProjet char(1),
     constraint ID_Personnel_ID primary key (id_personnel));

create table Projet (
     id_projet char(1) not null,
     nom_projet char(1) not null,
     statut char(1) not null,
     date_debut char(1) not null,
     date_fin char(1) not null,
     montant_total_estime char(1) not null,
     type_marche char(1) not null,
     id_client char(1) not null,
     id_cout char(1) not null,
     id_phase char(1) not null,
     ID_Fac numeric(10) not null,
     constraint ID_Projet_ID primary key (id_projet));

create table Client (
     id_client varchar(10) not null,
     nom_client varchar(100) not null,
     adresse TEXT not null,
     secteur_activite varchar(100) not null,
     constraint ID_Client_ID primary key (id_client));

create table Gerer (
     id_personnel char(1) not null,
     id_projet char(1) not null,
     constraint ID_Gerer_ID primary key (id_personnel, id_projet));


-- Constraints Section
-- ___________________ 

alter table Collaborateur add constraint FKResponsable_FK
     foreign key (id_tache -- Compound attribute --)
     references Tache;

alter table Collaborateur add constraint FKPer_Col_FK
     foreign key (id_personnel)
     references Personnel;

alter table Comptable add constraint FKPer_Com_FK
     foreign key (id_personnel)
     references Personnel;

alter table ChefProjet add constraint FKPer_Che_CHK
     check(exists(select * from Gerer
                  where Gerer.id_personnel = id_personnel)); 

alter table ChefProjet add constraint FKPer_Che_FK
     foreign key (id_personnel)
     references Personnel;

alter table Phase add constraint ID_Phase_CHK
     check(exists(select * from Tache
                  where Tache.id_phase = id_phase)); 

alter table Phase add constraint FKDetailler_FK
     foreign key (ID_Fac)
     references Facture;

alter table Tache add constraint ID_Tache_CHK
     check(exists(select * from Collaborateur
                  where Collaborateur.id_tache = id_tache)); 

alter table Tache add constraint FKInclure_FK
     foreign key (id_phase)
     references Phase;

alter table Personnel add constraint LSTONE_Personnel
     check(Comptable is not null or ChefProjet is not null or Collaborateur is not null); 

alter table Projet add constraint FKCommander_FK
     foreign key (id_client)
     references Client;

alter table Projet add constraint FKAssocier_FK
     foreign key (id_cout)
     references Cout;

alter table Projet add constraint FKComposer_FK
     foreign key (id_phase)
     references Phase;

alter table Projet add constraint FKFacturer_FK
     foreign key (ID_Fac)
     references Facture;

alter table Gerer add constraint FKGer_Pro_FK
     foreign key (id_projet)
     references Projet;

alter table Gerer add constraint FKGer_Che
     foreign key (id_personnel)
     references ChefProjet;


-- Index Section
-- _____________ 

create unique index ID_IND
     on Facture (ID_Fac);

create unique index ID_Cout_IND
     on Cout (id_cout);

create unique index ID_ImportLog_IND
     on ImportLog (id_import);

create unique index FKResponsable_IND
     on Collaborateur (id_tache -- Compound attribute --);

create unique index FKPer_Col_IND
     on Collaborateur (id_personnel);

create unique index FKPer_Com_IND
     on Comptable (id_personnel);

create unique index FKPer_Che_IND
     on ChefProjet (id_personnel);

create unique index ID_Planification_IND
     on Planification (id_planification);

create unique index ID_Prestation_IND
     on Prestation (id_prestation);

create unique index ID_Phase_IND
     on Phase (id_phase);

create index FKDetailler_IND
     on Phase (ID_Fac);

create unique index ID_Tache_IND
     on Tache (id_tache -- Compound attribute --);

create unique index FKInclure_IND
     on Tache (id_phase);

create unique index ID_Personnel_IND
     on Personnel (id_personnel);

create unique index ID_Projet_IND
     on Projet (id_projet);

create index FKCommander_IND
     on Projet (id_client);

create index FKAssocier_IND
     on Projet (id_cout);

create index FKComposer_IND
     on Projet (id_phase);

create index FKFacturer_IND
     on Projet (ID_Fac);

create unique index ID_Client_IND
     on Client (id_client);

create unique index ID_Gerer_IND
     on Gerer (id_personnel, id_projet);

create index FKGer_Pro_IND
     on Gerer (id_projet);

