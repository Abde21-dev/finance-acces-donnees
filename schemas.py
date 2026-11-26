from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

class SocieteEntree(BaseModel):
    """Données attendues pour créer ou remplacer une société."""

    model_config = ConfigDict(
        str_strip_whitespace=True,   # enlève les espaces au début et à la fin
        extra="forbid",              # refuse les champs inconnus
    )

    nom: str = Field(min_length=1, max_length=100, examples=["Atlas Mobilité"])
    symbole_boursier: str = Field(
        min_length=1, max_length=10, pattern=r"^[A-Z0-9.]+$", examples=["ATLM"],
    )
    secteur_activite: str = Field(min_length=1, max_length=50, examples=["Transport"])
    pays: str = Field(min_length=1, max_length=50, examples=["États-Unis"])
    devise: str = Field(default="EUR", pattern=r"^[A-Z]{3}$", examples=["USD"])

    @field_validator("symbole_boursier", "devise", mode="before")
    @classmethod
    def mettre_en_majuscules(cls, valeur):
        return valeur.strip().upper() if isinstance(valeur, str) else valeur


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