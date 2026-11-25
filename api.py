import logging
from datetime import date
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Path, Query, Request
from fastapi.responses import JSONResponse
from pymysql.connections import Connection

import acces_donnees
from connexion import ouvrir_connexion
from erreurs import ErreurMetier, SocieteIntrouvable, SocieteLiee, SymboleDejaUtilise
from schemas import BilanSortie, CoursSortie, Erreur, SocieteSortie

journal = logging.getLogger("api")

app = FastAPI(
    title="API Suivi financier",
    description="Accès aux sociétés cotées, à leurs bilans annuels et à leurs cours de bourse.",
    version="1.0.0",
)


# ---------- Connexion : une par demande, toujours fermée ----------

def get_connexion():
    connexion = ouvrir_connexion()
    try:
        yield connexion
    finally:
        connexion.close()


ConnexionBD = Annotated[Connection, Depends(get_connexion)]
IdSociete = Annotated[int, Path(gt=0, description="Identifiant de la société")]


# ---------- Traduction des erreurs en codes HTTP ----------

CODES_ERREURS = {
    SocieteIntrouvable: 404,
    SymboleDejaUtilise: 409,
    SocieteLiee: 409,
}


@app.exception_handler(ErreurMetier)
def gerer_erreur_metier(request: Request, erreur: ErreurMetier):
    code = CODES_ERREURS.get(type(erreur), 400)
    return JSONResponse(status_code=code, content={"detail": str(erreur)})


@app.exception_handler(Exception)
def gerer_erreur_imprevue(request: Request, erreur: Exception):
    # La trace complète va dans le terminal du serveur, jamais dans la réponse
    journal.exception("Erreur imprévue sur %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Erreur interne du serveur."})


# ---------- Routes ----------

@app.get("/", summary="Vérifier que l'API répond")
def accueil():
    return {"message": "API Suivi financier opérationnelle"}


@app.get(
    "/societes",
    response_model=list[SocieteSortie],
    summary="Lister les sociétés",
    description="Renvoie toutes les sociétés, classées par nom. Le paramètre `secteur` filtre sur un secteur d'activité.",
)
def lister_societes(connexion: ConnexionBD, secteur: Annotated[str | None, Query(max_length=50)] = None):
    return acces_donnees.lister_societes(connexion, secteur)


@app.get(
    "/societes/{societe_id}",
    response_model=SocieteSortie,
    summary="Lire une société",
    responses={404: {"model": Erreur, "description": "Société introuvable"}},
)
def lire_societe(connexion: ConnexionBD, societe_id: IdSociete):
    return acces_donnees.lire_societe_existante(connexion, societe_id)


@app.get(
    "/societes/{societe_id}/bilans",
    response_model=list[BilanSortie],
    summary="Lister les bilans d'une société",
    description="Renvoie les bilans annuels de la société, classés par année.",
    responses={404: {"model": Erreur, "description": "Société introuvable"}},
)
def lister_bilans(connexion: ConnexionBD, societe_id: IdSociete):
    acces_donnees.lire_societe_existante(connexion, societe_id)
    return acces_donnees.lister_bilans(connexion, societe_id)


@app.get(
    "/societes/{societe_id}/cours",
    response_model=list[CoursSortie],
    summary="Lister les cours d'une société",
    description="Renvoie les cours de clôture, classés par date. `debut` et `fin` (AAAA-MM-JJ) limitent la période.",
    responses={404: {"model": Erreur, "description": "Société introuvable"}},
)
def lister_cours(
    connexion: ConnexionBD,
    societe_id: IdSociete,
    debut: date | None = None,
    fin: date | None = None,
):
    if debut and fin and debut > fin:
        raise HTTPException(status_code=422, detail="La date de début doit précéder la date de fin.")
    acces_donnees.lire_societe_existante(connexion, societe_id)
    return acces_donnees.lister_cours(connexion, societe_id, debut, fin)