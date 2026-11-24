# Journal des erreurs

## Erreur : « La commande .env n'a pas été trouvée »
- **Cause** : j'ai tapé `.env` dans le terminal comme si c'était une commande, et j'étais dans le dossier `.venv`.
- **Solution** : revenir à la racine avec `cd ..`, puis créer le fichier avec `cp .env.example .env` ou depuis l'éditeur.

## Erreur : VS Code ne trouve pas l'interpréteur `.venv`
- **Cause** : j'avais ouvert un espace de travail avec plusieurs dossiers au lieu du dossier du projet.
- **Solution** : File → Close Workspace, puis File → Open Folder sur `finance-acces-donnees`.

## Erreur : « remote: Repository not found » au premier push
- **Cause** : je n'avais pas encore créé le dépôt sur GitHub.
- **Solution** : créer le dépôt sur GitHub (privé, sans README), puis relancer `git push -u origin main`.

## Erreur : «  err.raise_mysql_exception(self._data)» 
- **Cause** : File "/home/kaliabde/finance-acces-donnees/.venv/lib/python3.14/site-packages/pymysql/protocol.py", line 219, in raise_for_error
    err.raise_mysql_exception(self._data)
    ~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^
  File "/home/kaliabde/finance-acces-donnees/.venv/lib/python3.14/site-packages/pymysql/err.py", line 154, in raise_mysql_exception
    raise errorclass(errno, errval, sqlstate=sqlstate)
pymysql.err.IntegrityError: (1062, "Duplicate entry 'NRDB' for key 'symbole_boursier'")
- **Cause** : Cette société a déjà été créer
- **Solution** : C'est le comportement qui est attendu .
