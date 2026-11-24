from decimal import Decimal


class CalculImpossible(Exception):
    """Levée quand un indicateur ne peut pas être calculé (division par zéro, données insuffisantes...)."""


def _decimal(valeur):
    """Convertit une valeur en Decimal sans perte (str évite les imprécisions des float)."""
    return valeur if isinstance(valeur, Decimal) else Decimal(str(valeur))


def marge_nette(resultat_net, chiffre_affaires):
    """Marge nette = résultat net / chiffre d'affaires."""
    ca = _decimal(chiffre_affaires)
    if ca == 0:
        raise CalculImpossible("Marge nette impossible : le chiffre d'affaires est nul.")
    return _decimal(resultat_net) / ca


def liquidite(actifs_courants, passifs_courants):
    """Liquidité = actifs courants / passifs courants."""
    passifs = _decimal(passifs_courants)
    if passifs == 0:
        raise CalculImpossible("Liquidité impossible : les passifs courants sont nuls.")
    return _decimal(actifs_courants) / passifs


def endettement(dettes_totales, capitaux_propres):
    """Endettement = dettes totales / capitaux propres."""
    capitaux = _decimal(capitaux_propres)
    if capitaux == 0:
        raise CalculImpossible("Endettement impossible : les capitaux propres sont nuls.")
    if capitaux < 0:
        raise CalculImpossible("Endettement non significatif : les capitaux propres sont négatifs.")
    return _decimal(dettes_totales) / capitaux


def rendement(cours_precedent, cours_actuel):
    """Rendement en pourcentage entre deux cours : (actuel - précédent) / précédent * 100."""
    precedent = _decimal(cours_precedent)
    if precedent == 0:
        raise CalculImpossible("Rendement impossible : le cours précédent est nul.")
    return (_decimal(cours_actuel) - precedent) / precedent * 100


def moyenne_mobile(cours, fenetre):
    """Moyenne mobile des cours sur une fenêtre de n jours.
    Renvoie une liste : une moyenne pour chaque jour à partir du n-ième."""
    if not isinstance(fenetre, int) or fenetre <= 0:
        raise CalculImpossible("Moyenne mobile impossible : la fenêtre doit être un entier positif.")
    if len(cours) < fenetre:
        raise CalculImpossible(
            f"Moyenne mobile impossible : {len(cours)} cours disponibles pour une fenêtre de {fenetre} jours."
        )
    valeurs = [_decimal(c) for c in cours]
    return [
        sum(valeurs[i - fenetre + 1 : i + 1]) / fenetre
        for i in range(fenetre - 1, len(valeurs))
    ]