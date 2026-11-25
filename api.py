from fastapi import FastAPI

app = FastAPI(
    title="API Suivi financier",
    description="Accès aux sociétés cotées, à leurs bilans annuels et à leurs cours de bourse.",
    version="1.0.0",
)


@app.get("/", summary="Vérifier que l'API répond")
def accueil():
    return {"message": "API Suivi financier opérationnelle"}