from connexion import ouvrir_connexion
from modeles import Societe, Bilan, Cours

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

SQL_AJOUTER_SOCIETE = """
    INSERT INTO societes (nom, symbole_boursier, secteur_activite, pays)
    VALUES (%s, %s, %s, %s)
"""

SQL_LISTER_BILANS = """
    SELECT id, societe_id, annee, chiffre_affaires, resultat_net,
           actifs_courants, passifs_courants, dettes_totales,
           capitaux_propres, total_actifs
    FROM bilans
    WHERE societe_id = %s
    ORDER BY annee
"""

SQL_LISTER_COURS_PERIODE = """
    SELECT id, societe_id, date_cours, cours_cloture, volume_echange
    FROM cours_bourse
    WHERE societe_id = %s
      AND date_cours BETWEEN %s AND %s
    ORDER BY date_cours
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

def ajouter_societe(societe):
    """Enregistre une nouvelle société et la renvoie avec son identifiant.
    La modification est validée si tout se passe bien, annulée sinon."""
    connexion = ouvrir_connexion()
    try:
        with connexion.cursor() as curseur:
            curseur.execute(
                SQL_AJOUTER_SOCIETE,
                (societe.nom, societe.symbole_boursier,
                 societe.secteur_activite, societe.pays),
            )
            nouvel_id = curseur.lastrowid
        connexion.commit()
        return Societe(
            id=nouvel_id,
            nom=societe.nom,
            symbole_boursier=societe.symbole_boursier,
            secteur_activite=societe.secteur_activite,
            pays=societe.pays,
        )
    except Exception:
        connexion.rollback()
        raise
    finally:
        connexion.close()


def lister_bilans(societe_id):
    """Renvoie les bilans d'une société, classés par année."""
    connexion = ouvrir_connexion()
    try:
        with connexion.cursor() as curseur:
            curseur.execute(SQL_LISTER_BILANS, (societe_id,))
            lignes = curseur.fetchall()
        return [Bilan(**ligne) for ligne in lignes]
    finally:
        connexion.close()


def lister_cours(societe_id, date_debut, date_fin):
    """Renvoie les cours d'une société entre deux dates incluses, classés par date."""
    connexion = ouvrir_connexion()
    try:
        with connexion.cursor() as curseur:
            curseur.execute(SQL_LISTER_COURS_PERIODE, (societe_id, date_debut, date_fin))
            lignes = curseur.fetchall()
        return [Cours(**ligne) for ligne in lignes]
    finally:
        connexion.close()        