import os
from dotenv import load_dotenv

load_dotenv()


def _obligatoire(nom):
    """Renvoie la valeur d'une variable, ou arrête le programme avec un message clair."""
    valeur = os.getenv(nom)
    if not valeur:
        raise RuntimeError(f"Variable d'environnement manquante : {nom} (voir .env.example)")
    return valeur


DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = _obligatoire("DB_NAME")
DB_USER = _obligatoire("DB_USER")
DB_PASSWORD = _obligatoire("DB_PASSWORD")