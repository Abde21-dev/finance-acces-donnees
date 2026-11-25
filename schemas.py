from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class SocieteSortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom: str
    symbole_boursier: str
    secteur_activite: str
    pays: str
    devise: str


class BilanSortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    annee: int
    chiffre_affaires: Decimal
    resultat_net: Decimal
    actifs_courants: Decimal
    passifs_courants: Decimal
    dettes_totales: Decimal
    capitaux_propres: Decimal
    total_actifs: Decimal


class CoursSortie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date_cours: date
    cours_cloture: Decimal
    volume_echange: int


class Erreur(BaseModel):
    detail: str