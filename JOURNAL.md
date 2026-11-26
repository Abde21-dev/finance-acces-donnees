# Journal des erreurs

## Erreur : La commande .env n'a pas été trouvée 
- **Cause** : j'ai tapé `.env` dans le terminal comme si c'était une commande, et j'étais dans le dossier `.venv`.
- **Solution** : revenir à la racine avec `cd ..`, puis créer le fichier avec `cp .env.example .env` ou depuis l'éditeur.

## Erreur : VS Code ne trouve pas l'interpréteur `.venv`
- **Cause** : j'avais ouvert un espace de travail avec plusieurs dossiers au lieu du dossier du projet.
- **Solution** : File → Close Workspace, puis File → Open Folder sur `finance-acces-donnees`.

## Erreur : remote: Repository not found  au premier push
- **Cause** : je n'avais pas encore créé le dépôt sur GitHub.
- **Solution** : créer le dépôt sur GitHub (privé, sans README), puis relancer `git push -u origin main`.

## Erreur :  err.raise_mysql_exception(self._data)
- **Cause** : File "/home/kaliabde/finance-acces-donnees/.venv/lib/python3.14/site-packages/pymysql/protocol.py", line 219, in raise_for_error
    err.raise_mysql_exception(self._data)
    ~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^
  File "/home/kaliabde/finance-acces-donnees/.venv/lib/python3.14/site-packages/pymysql/err.py", line 154, in raise_mysql_exception
    raise errorclass(errno, errval, sqlstate=sqlstate)
pymysql.err.IntegrityError: (1062, "Duplicate entry 'NRDB' for key 'symbole_boursier'")
- **Cause** : Cette société a déjà été créer
- **Solution** : C'est le comportement qui est attendu .

## Erreur : NameError: name 'liquidite' is not defined
- **Cause** : j'avais relancé l'interpréteur Python, qui avait oublié l'import précédent.
- **Solution** : refaire `from indicateurs import *` à chaque nouveau lancement de `python`.

SHOW GRANTS affiche exactement ces droits :
+--------------------------------------------------------------------------------------------------------------------+
| Grants for app_finance@localhost                                                                                   |
+--------------------------------------------------------------------------------------------------------------------+
| GRANT USAGE ON *.* TO `app_finance`@`localhost` IDENTIFIED BY PASSWORD '*92EBCFFCD2888227B7B5728FD7E84CB41FE4ADF2' |
| GRANT SELECT ON `finance`.`cours_bourse` TO `app_finance`@`localhost`                                              |
| GRANT SELECT ON `finance`.`bilans` TO `app_finance`@`localhost`                                                    |
| GRANT SELECT, INSERT ON `finance`.`societes` TO `app_finance`@`localhost`                                          |
+--------------------------------------------------------------------------------------------------------------------+

## Sécurité : compte dédié
- Compte `app_finance` créé avec seulement : SELECT et INSERT sur `societes`,
  SELECT sur `bilans` et `cours_bourse`.
- Test : `DELETE FROM societes` avec ce compte → refusé
  (« DELETE command denied to user 'app_finance'@'localhost' »).
- Les commandes de création du compte ne sont pas dans le dépôt, pour ne pas
  y mettre de mot de passe.

  $ mariadb -u app_finance -p finance -e "DELETE FROM societes;"
Enter password: 
--------------
DELETE FROM societes
--------------

ERROR 1142 (42000) at line 1: DELETE command denied to user 'app_finance'@'localhost' for table `finance`.`societes`

## Sécurité : saisie piégée
- Test : `lister_societes("' OR '1'='1")` → `[]`, aucune donnée renvoyée.
- Explication : la requête utilise un paramètre `%s`, donc la saisie est traitée
  comme une valeur et jamais comme du SQL.
- Contre-exemple (non conservé dans le code) : avec une concaténation, la même
  saisie renvoyait toutes les sociétés.

  >>> from acces_donnees import lister_societes
>>> lister_societes("Énergie") 
[Societe(id=1, nom='Solaria Énergie', symbole_boursier='SOLR', secteur_activite='Énergie', pays='France')]
>>> lister_societes("' OR '1'='1")
[]

# Test de cas limimite :
└─$ python main.py 99
Aucune société avec l'identifiant 99.

# Test d'authentification :
└─$ python main.py abc
Identifiant invalide : « abc » (un nombre entier est attendu).

# Test d'intrusion : 
└─$ python main.py ' OR 1=1 --'                                 
Identifiant invalide : «  OR 1=1 -- » (un nombre entier est attendu)

# Commandes 
from datetime import date
from acces_donnees import lister_societes, lister_bilans, lister_cours
lister_societes()

# Résultat
[Societe(id=3, nom='Medivita Santé', symbole_boursier='MDVT', secteur_activite='Santé', pays='Suisse'), Societe(id=2, nom='Nordia Banque', symbole_boursier='NRDB', secteur_activite='Finance', pays='Belgique'), Societe(id=4, nom='Pixelwave Studios', symbole_boursier='PXLW', secteur_activite='Technologie', pays='Canada'), Societe(id=1, nom='Solaria Énergie', symbole_boursier='SOLR', secteur_activite='Énergie', pays='France')]

## Évolution 002 : ajout de la devise
- Commande : `sudo mariadb < sql/002_ajout_devise.sql`
- Résultat : la colonne `devise` est ajoutée, et les 4 sociétés existantes
  ont reçu `EUR` automatiquement grâce au `DEFAULT`.
- Données conservées : 4 sociétés, 12 bilans et 40 cours avant et après l'évolution.

```
+----+-------------------+--------+
| id | nom               | devise |
+----+-------------------+--------+
|  1 | Solaria Énergie   | EUR    |
|  2 | Nordia Banque     | EUR    |
|  3 | Medivita Santé    | EUR    |
|  4 | Pixelwave Studios | EUR    |
+----+-------------------+--------+
```

## Erreur : ProgrammingError: not all arguments converted during string formatting
- **Cause** : après l'ajout de la devise, la fonction envoyait 5 paramètres,
  mais la requête INSERT n'avait que 4 `%s`.
- **Solution** : ajouter la colonne `devise` et un 5e `%s` dans `SQL_AJOUTER_SOCIETE`,
  puis relancer l'interpréteur Python pour recharger le fichier.
- **À retenir** : il doit toujours y avoir autant de `%s` que de valeurs dans le tuple.exit()

## Installation de la base (compte administrateur)

    sudo mariadb < sql/001_creation.sql
    sudo mariadb < sql/002_ajout_devise.sql
    sudo mariadb < sql/jeu_de_test.sql

Puis créer le compte applicatif `app_finance` (voir la section Sécurité)
et renseigner ses identifiants dans `.env` (modèle : `.env.example`).

_______

# Journal des erreurs - Projet API REST FastAPI

### 1. Erreur d'environnement virtuel (PEP 668)
* **Problème :** `error: externally-managed-environment` lors de l'installation de FastAPI et Uvicorn avec `pip install`.
* **Cause :** Sécurité de Kali Linux interdisant l'installation de paquets Python globaux.
* **Solution :** Activation de l'environnement virtuel avec `source .venv/bin/activate` avant d'exécuter `pip install`.

### 2. Erreur d'importation des fonctions de modification
* **Problème :** `ImportError: cannot import name 'modifier_societe' from 'acces_donnees'`.
* **Cause :** Mauvaise indentation des fonctions `modifier_societe` et `supprimer_societe` dans le fichier `acces_donnees.py` (elles étaient imbriquées à l'intérieur de la fonction précédente).
* **Solution :** Remise au niveau de la racine du fichier des deux fonctions.

### 3. Gestion des conflits de base de données (Code 409)
* **Problème :** L'API renvoyait une erreur 500 brute en cas de doublon de symbole boursier ou de suppression d'une société liée à des bilans.
* **Cause :** Les exceptions `pymysql.err.IntegrityError` n'étaient pas interceptées et traduites en codes HTTP.
* **Solution :** Utilisation de blocs `try/except pymysql.err.IntegrityError` dans l'API pour renvoyer proprement un code `409 Conflict` avec un message clair.

