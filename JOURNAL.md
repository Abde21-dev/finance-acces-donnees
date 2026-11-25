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