from connexion import ouvrir_connexion
from modeles import Societe

# ---------- Requêtes SQL (toutes regroupées ici) ----------

SQL_LISTER_SOCIETES = """
    SELECT id, nom, symbole_boursier, secteur_activite, pays
    FROM societes
    ORDER BY nom
"""

SQL_LISTER_SOCIETES_PAR_SECTEUR = """
    SELECT id, nom, symbole_boursier, secteur_activite, pays
    FROM societes
    WHERE secteur_activite = %s
    ORDER BY nom
"""

SQL_LIRE_SOCIETE = """
    SELECT id, nom, symbole_boursier, secteur_activite, pays
    FROM societes
    WHERE id = %s
"""


# ---------- Fonctions d'accès ----------

def lister_societes(secteur=None):
    """Renvoie la liste des sociétés, éventuellement filtrée sur un secteur."""
    connexion = ouvrir_connexion()
    try:
        with connexion.cursor() as curseur:
            if secteur is None:
                curseur.execute(SQL_LISTER_SOCIETES)
            else:
                curseur.execute(SQL_LISTER_SOCIETES_PAR_SECTEUR, (secteur,))
            lignes = curseur.fetchall()
        return [Societe(**ligne) for ligne in lignes]
    finally:
        connexion.close()


def lire_societe(societe_id):
    """Renvoie la société correspondant à l'identifiant, ou None si elle n'existe pas."""
    connexion = ouvrir_connexion()
    try:
        with connexion.cursor() as curseur:
            curseur.execute(SQL_LIRE_SOCIETE, (societe_id,))
            ligne = curseur.fetchone()
        return Societe(**ligne) if ligne else None
    finally:
        connexion.close()