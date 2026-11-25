import sys
from datetime import date

from acces_donnees import lire_societe, lister_bilans, lister_cours
from indicateurs import (
    CalculImpossible,
    endettement,
    liquidite,
    marge_nette,
    moyenne_mobile,
    rendement,
)

SOCIETE_PAR_DEFAUT = 1
FENETRE_MOYENNE_MOBILE = 5
DATE_DEBUT_COURS = date(2000, 1, 1)


# ---------- Mise en forme ----------

def montant(valeur, devise):
    """1275000000.00 -> '1 275 000 000,00 EUR'"""
    texte = f"{valeur:,.2f}".replace(",", " ").replace(".", ",")
    return f"{texte} {devise}"


def nombre(valeur, decimales=2):
    """1.2753 -> '1,28'"""
    return f"{valeur:.{decimales}f}".replace(".", ",")


def afficher_indicateur(libelle, calcul):
    """Affiche le résultat d'un calcul, ou le message clair s'il est impossible."""
    try:
        print(f"  {libelle:<22}: {calcul()}")
    except CalculImpossible as erreur:
        print(f"  {libelle:<22}: non calculable ({erreur})")


# ---------- Les trois parties de la démonstration ----------

def afficher_societe(societe):
    print(f"=== {societe.nom} ({societe.symbole_boursier}) ===")
    print(f"  Secteur : {societe.secteur_activite}")
    print(f"  Pays    : {societe.pays}")
    print(f"  Devise  : {societe.devise}")


def afficher_indicateurs(societe, bilans, cours):
    print()
    if not bilans:
        print("Indicateurs : aucun bilan enregistré pour cette société.")
    else:
        dernier = bilans[-1]   # les bilans sont classés par année croissante
        print(f"Indicateurs de l'année {dernier.annee}")
        print(f"  Chiffre d'affaires    : {montant(dernier.chiffre_affaires, societe.devise)}")
        print(f"  Résultat net          : {montant(dernier.resultat_net, societe.devise)}")
        afficher_indicateur(
            "Marge nette",
            lambda: nombre(marge_nette(dernier.resultat_net, dernier.chiffre_affaires) * 100) + " %",
        )
        afficher_indicateur(
            "Liquidité",
            lambda: nombre(liquidite(dernier.actifs_courants, dernier.passifs_courants)),
        )
        afficher_indicateur(
            "Endettement",
            lambda: nombre(endettement(dernier.dettes_totales, dernier.capitaux_propres)),
        )

    # Rendement entre les deux derniers jours de cours
    if len(cours) < 2:
        print("  Rendement             : non calculable (moins de deux cours enregistrés)")
    else:
        avant, apres = cours[-2], cours[-1]
        afficher_indicateur(
            f"Rendement au {apres.date_cours:%d/%m}",
            lambda: f"{rendement(avant.cours_cloture, apres.cours_cloture):+.2f} %".replace(".", ","),
        )


def afficher_moyenne_mobile(societe, cours):
    print()
    print(f"Moyenne mobile sur {FENETRE_MOYENNE_MOBILE} jours")
    try:
        valeurs = [c.cours_cloture for c in cours]
        moyennes = moyenne_mobile(valeurs, FENETRE_MOYENNE_MOBILE)
    except CalculImpossible as erreur:
        print(f"  non calculable ({erreur})")
        return

    # La 1re moyenne correspond au n-ième jour de cours, la suivante au jour d'après, etc.
    jours = cours[FENETRE_MOYENNE_MOBILE - 1:]
    for jour, moyenne in zip(jours, moyennes):
        print(f"  {jour.date_cours:%d/%m/%Y}  cours {nombre(jour.cours_cloture):>8}"
              f"   moyenne {nombre(moyenne):>8}")


# ---------- Programme principal ----------

def main():
    # Identifiant de la société : premier argument, sinon la société par défaut
    if len(sys.argv) > 1:
        try:
            societe_id = int(sys.argv[1])
        except ValueError:
            print(f"Identifiant invalide : « {sys.argv[1]} » (un nombre entier est attendu).")
            return
    else:
        societe_id = SOCIETE_PAR_DEFAUT

    societe = lire_societe(societe_id)
    if societe is None:
        print(f"Aucune société avec l'identifiant {societe_id}.")
        return

    bilans = lister_bilans(societe.id)
    cours = lister_cours(societe.id, DATE_DEBUT_COURS, date.today())

    afficher_societe(societe)
    afficher_indicateurs(societe, bilans, cours)
    afficher_moyenne_mobile(societe, cours)


if __name__ == "__main__":
    main()