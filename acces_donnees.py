from datetime import date

import pymysql

from erreurs import SocieteIntrouvable, SymboleDejaUtilise
from modeles import Bilan, Cours, Societe

# Codes d'erreur MariaDB utilisés
ERREUR_DOUBLON = 1062

# Bornes des dates acceptées par MariaDB, utilisées quand aucune période n'est donnée
DATE_MIN = date(1000, 1, 1)
DATE_MAX = date(9999, 12, 31)

# ---------- Requêtes SQL (toutes regroupées ici) ----------

SQL_LISTER_SOCIETES = """
    SELECT id, nom, symbole_boursier, secteur_activite, pays, devise
    FROM societes
    ORDER BY nom
"""

SQL_LISTER_SOCIETES_PAR_SECTEUR = """
    SELECT id, nom, symbole_boursier, secteur_activite, pays, devise
    FROM societes
    WHERE secteur_activite = %s
    ORDER BY nom
"""

SQL_LIRE_SOCIETE = """
    SELECT id, nom, symbole_boursier, secteur_activite, pays, devise
    FROM societes
    WHERE id = %s
"""

SQL_AJOUTER_SOCIETE = """
    INSERT INTO societes (nom, symbole_boursier, secteur_activite, pays, devise)
    VALUES (%s, %s, %s, %s, %s)
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


# ---------- Sociétés ----------

def lister_societes(connexion, secteur=None):
    """Renvoie la liste des sociétés, éventuellement filtrée sur un secteur."""
    with connexion.cursor() as curseur:
        if secteur is None:
            curseur.execute(SQL_LISTER_SOCIETES)
        else:
            curseur.execute(SQL_LISTER_SOCIETES_PAR_SECTEUR, (secteur,))
        return [Societe(**ligne) for ligne in curseur.fetchall()]


def lire_societe(connexion, societe_id):
    """Renvoie la société, ou None si elle n'existe pas."""
    with connexion.cursor() as curseur:
        curseur.execute(SQL_LIRE_SOCIETE, (societe_id,))
        ligne = curseur.fetchone()
    return Societe(**ligne) if ligne else None


def lire_societe_existante(connexion, societe_id):
    """Renvoie la société, ou lève SocieteIntrouvable si elle n'existe pas."""
    societe = lire_societe(connexion, societe_id)
    if societe is None:
        raise SocieteIntrouvable(societe_id)
    return societe


def ajouter_societe(connexion, societe):
    """Enregistre une société et la renvoie avec son identifiant.
    Valide la modification si tout se passe bien, l'annule sinon."""
    try:
        with connexion.cursor() as curseur:
            curseur.execute(
                SQL_AJOUTER_SOCIETE,
                (societe.nom, societe.symbole_boursier,
                 societe.secteur_activite, societe.pays, societe.devise),
            )
            nouvel_id = curseur.lastrowid
        connexion.commit()
    except pymysql.err.IntegrityError as erreur:
        connexion.rollback()
        if erreur.args[0] == ERREUR_DOUBLON:
            raise SymboleDejaUtilise(societe.symbole_boursier) from None
        raise
    except Exception:
        connexion.rollback()
        raise
    return Societe(
        id=nouvel_id,
        nom=societe.nom,
        symbole_boursier=societe.symbole_boursier,
        secteur_activite=societe.secteur_activite,
        pays=societe.pays,
        devise=societe.devise,
    )


# ---------- Bilans et cours ----------

def lister_bilans(connexion, societe_id):
    """Renvoie les bilans d'une société, classés par année."""
    with connexion.cursor() as curseur:
        curseur.execute(SQL_LISTER_BILANS, (societe_id,))
        return [Bilan(**ligne) for ligne in curseur.fetchall()]


def lister_cours(connexion, societe_id, date_debut=None, date_fin=None):
    """Renvoie les cours d'une société entre deux dates incluses (toutes les dates par défaut)."""
    with connexion.cursor() as curseur:
        curseur.execute(
            SQL_LISTER_COURS_PERIODE,
            (societe_id, date_debut or DATE_MIN, date_fin or DATE_MAX),
        )
        return [Cours(**ligne) for ligne in curseur.fetchall()]