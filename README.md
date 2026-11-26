# Finance – couche d'accès aux données

Couche d'accès Python à une base MariaDB : sociétés cotées, bilans annuels et cours de bourse.
Elle lit et ajoute des données de façon sécurisée et calcule cinq indicateurs financiers.

## Structure
- `config.py` : lecture de la configuration (variables d'environnement)
- `connexion.py` : ouverture de la connexion MariaDB
- `modeles.py` : objets `Societe`, `Bilan`, `Cours`
- `acces_donnees.py` : toutes les requêtes SQL de l'application
- `indicateurs.py` : calculs financiers, sans accès à la base
- `main.py` : programme de démonstration
- `sql/` : création de la base (001), évolution devise (002), jeu de test
- `JOURNAL.md` : erreurs rencontrées, solutions et tests de sécurité

## Installation
    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt

## Base de données (compte administrateur, dans cet ordre)
    sudo mariadb < sql/001_creation.sql
    sudo mariadb < sql/002_ajout_devise.sql
    sudo mariadb < sql/jeu_de_test.sql

Créer ensuite, dans `sudo mariadb`, le compte `app_finance` avec seulement :
`SELECT, INSERT, UPDATE, DELETE` sur `societes` et `SELECT` sur `bilans` et `cours_bourse`.

## Configuration
Copier `.env.example` en `.env`, puis renseigner les identifiants de `app_finance`.
Le fichier `.env` est ignoré par Git.

## Utilisation
    python main.py [id_societe]

Affiche les informations de la société, ses indicateurs de la dernière année et la moyenne mobile de ses cours.

## Fonctionnalités
- Accès : lister les sociétés (filtre facultatif par secteur), lire une société, ajouter une société,
  lister les bilans d'une société, lister ses cours sur une période. Les fonctions renvoient des objets Python.
- Indicateurs : marge nette, liquidité, endettement, rendement, moyenne mobile.
  Un calcul impossible lève `CalculImpossible` avec un message clair.

## Sécurité
- Requêtes paramétrées (`%s`) : la saisie `' OR '1'='1` ne renvoie aucune donnée.
- Compte dédié aux droits minimum, jamais le compte administrateur.
- Aucun mot de passe dans le code ni dans l'historique Git.
- Toute modification est validée (`commit`) ou annulée (`rollback`) en cas d'erreur.

## Lancer l'API
    uvicorn api:app --reload
Documentation interactive : http://127.0.0.1:8000/docs