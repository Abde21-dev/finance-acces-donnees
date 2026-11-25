-- Évolution 002 : ajout de la devise de chaque société
-- Prérequis : 001_creation.sql déjà exécuté
-- Utilisation : sudo mariadb < sql/002_ajout_devise.sql

USE finance;

ALTER TABLE societes
    ADD COLUMN IF NOT EXISTS devise CHAR(3) NOT NULL DEFAULT 'EUR';