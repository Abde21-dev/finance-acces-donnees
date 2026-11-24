DROP DATABASE IF EXISTS finance;
CREATE DATABASE finance CHARACTER SET utf8mb4;
USE finance;

CREATE TABLE societes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    symbole_boursier VARCHAR(10) NOT NULL UNIQUE,
    secteur_activite VARCHAR(50) NOT NULL,
    pays VARCHAR(50) NOT NULL
);

CREATE TABLE bilans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    societe_id INT NOT NULL,
    annee SMALLINT NOT NULL,
    chiffre_affaires DECIMAL(15,2) NOT NULL CHECK (chiffre_affaires >= 0),
    resultat_net DECIMAL(15,2) NOT NULL,
    actifs_courants DECIMAL(15,2) NOT NULL CHECK (actifs_courants >= 0),
    passifs_courants DECIMAL(15,2) NOT NULL CHECK (passifs_courants >= 0),
    dettes_totales DECIMAL(15,2) NOT NULL CHECK (dettes_totales >= 0),
    capitaux_propres DECIMAL(15,2) NOT NULL,
    total_actifs DECIMAL(15,2) NOT NULL CHECK (total_actifs >= 0),
    UNIQUE (societe_id, annee),
    FOREIGN KEY (societe_id) REFERENCES societes(id)
);

CREATE TABLE cours_bourse (
    id INT AUTO_INCREMENT PRIMARY KEY,
    societe_id INT NOT NULL,
    date_cours DATE NOT NULL,
    cours_cloture DECIMAL(15,2) NOT NULL CHECK (cours_cloture > 0),
    volume_echange BIGINT NOT NULL CHECK (volume_echange >= 0),
    UNIQUE (societe_id, date_cours),
    FOREIGN KEY (societe_id) REFERENCES societes(id)
);