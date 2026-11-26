from datetime import date
from typing import Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
import pymysql

from acces_donnees import (
    ajouter_societe,
    lire_societe,
    lister_bilans,
    lister_cours,
    lister_societes,
    modifier_societe,
    supprimer_societe,
)
from modeles import Societe

app = FastAPI(
    title="API Analyse Financière",
    description="API REST pour la gestion des sociétés, bilans et cours boursiers.",
    version="1.0.0",
)


# ---------- Modèles de validation Pydantic ----------
class SocieteEntree(BaseModel):
    nom: str = Field(..., min_length=1, max_length=100, description="Nom de la société")
    symbole_boursier: str = Field(..., min_length=1, max_length=10, description="Symbole boursier unique")
    secteur_activite: str = Field(..., max_length=60, description="Secteur d'activité")
    pays: str = Field(..., max_length=60, description="Pays d'implantation")
    devise: str = Field(default="EUR", max_length=3, description="Devise (ex: EUR)")


# ---------- Routes : Sociétés ----------

@app.get(
    "/societes",
    response_model=list[Societe],
    status_code=status.HTTP_200_OK,
    summary="Lister les sociétés"
)
def get_societes(secteur: Optional[str] = None):
    """Renvoie la liste de toutes les sociétés, avec un filtre facultatif par secteur."""
    try:
        return lister_societes(secteur=secteur)
    except Exception:
        raise HTTPException(status_code=500, detail="Erreur interne.")


@app.get(
    "/societes",
    response_model=list[Societe],
    status_code=status.HTTP_200_OK,
    summary="Lister les sociétés",
)
def get_societes(secteur: Optional[str] = None):
  """Renvoie la liste de toutes les sociétés, avec un filtre facultatif par secteur."""
  try:
    return lister_societes(secteur=secteur)
  except Exception as e:
    # On affiche l'erreur exacte pour le debug
    raise HTTPException(status_code=500, detail=f"Erreur technique : {str(e)}")


@app.post(
    "/societes",
    response_model=Societe,
    status_code=status.HTTP_201_CREATED,
    summary="Créer une société"
)
def post_societe(societe: SocieteEntree):
    """Crée une nouvelle société. Renvoie 409 si le symbole existe déjà."""
    try:
        nouvelle = Societe(
            id=None,
            nom=societe.nom,
            symbole_boursier=societe.symbole_boursier,
            secteur_activite=societe.secteur_activite,
            pays=societe.pays,
            devise=societe.devise,
        )
        return ajouter_societe(nouvelle)
    except pymysql.err.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Conflit : ce symbole boursier est déjà utilisé."
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Erreur interne.")


@app.put(
    "/societes/{societe_id}",
    response_model=Societe,
    status_code=status.HTTP_200_OK,
    summary="Remplacer une société"
)
def put_societe(societe_id: int, societe: SocieteEntree):
    """Remplace entièrement les informations d'une société existante."""
    existante = lire_societe(societe_id)
    if not existante:
        raise HTTPException(status_code=404, detail="Société introuvable.")

    try:
        societe_maj = Societe(
            id=societe_id,
            nom=societe.nom,
            symbole_boursier=societe.symbole_boursier,
            secteur_activite=societe.secteur_activite,
            pays=societe.pays,
            devise=societe.devise,
        )
        modifier_societe(societe_id, societe_maj)
        return societe_maj
    except pymysql.err.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Conflit : ce symbole boursier est déjà utilisé."
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Erreur interne.")


@app.delete(
    "/societes/{societe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer une société"
)
def delete_societe(societe_id: int):
    """Supprime une société (404 si absente, 409 si des bilans sont liés)."""
    existante = lire_societe(societe_id)
    if not existante:
        raise HTTPException(status_code=404, detail="Société introuvable.")

    try:
        supprimer_societe(societe_id)
        return None
    except pymysql.err.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Conflit : impossible de supprimer la société (bilans rattachés)."
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Erreur interne.")


# ---------- Routes : Bilans & Cours (Lecture hiérarchisée) ----------

@app.get(
    "/societes/{societe_id}/bilans",
    status_code=status.HTTP_200_OK,
    summary="Lister les bilans d'une société"
)
def get_bilans_societe(societe_id: int):
    """Renvoie la liste des bilans financiers d'une société."""
    societe = lire_societe(societe_id)
    if not societe:
        raise HTTPException(status_code=404, detail="Société introuvable.")
    return lister_bilans(societe_id)


@app.get(
    "/societes/{societe_id}/cours",
    status_code=status.HTTP_200_OK,
    summary="Lister les cours boursiers d'une société"
)
def get_cours_societe(
    societe_id: int,
    date_debut: Optional[date] = date(2000, 1, 1),
    date_fin: Optional[date] = date.today(),
):
    """Renvoie les cours boursiers d'une société sur une période donnée."""
    societe = lire_societe(societe_id)
    if not societe:
        raise HTTPException(status_code=404, detail="Société introuvable.")
    return lister_cours(societe_id, date_debut, date_fin)