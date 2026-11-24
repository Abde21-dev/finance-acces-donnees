import pymysql
from pymysql.cursors import DictCursor

import config


def ouvrir_connexion():
    """Ouvre une connexion à la base MariaDB à partir de la configuration."""
    return pymysql.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=False,
    )