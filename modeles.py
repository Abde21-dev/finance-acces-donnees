from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional


@dataclass
class Societe:
    id: Optional[int]          # None tant que la société n'est pas encore en base
    nom: str
    symbole_boursier: str
    secteur_activite: str
    pays: str


@dataclass
class Bilan:
    id: int
    societe_id: int
    annee: int
    chiffre_affaires: Decimal
    resultat_net: Decimal
    actifs_courants: Decimal
    passifs_courants: Decimal
    dettes_totales: Decimal
    capitaux_propres: Decimal
    total_actifs: Decimal


@dataclass
class Cours:
    id: int
    societe_id: int
    date_cours: date
    cours_cloture: Decimal
    volume_echange: int