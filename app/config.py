from decouple import config
from urllib.parse import quote_plus
from datetime import timedelta
import pyodbc

def _pick_driver():
    prefer = config("SQL_DRIVER", default="ODBC Driver 18 for SQL Server")
    installed = set(pyodbc.drivers())
    if prefer in installed:
        return prefer
    for cand in ("ODBC Driver 18 for SQL Server", "ODBC Driver 17 for SQL Server", "SQL Server"):
        if cand in installed:
            return cand
    raise RuntimeError(f"No hay driver ODBC de SQL Server instalado. Vistos: {installed}")

class Config():
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = config("SECRET_KEY")
    JWT_SECRET_KEY = config("JWT_SECRET")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=20, minutes=30)
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"

class DevelopmentConfig(Config):
    DEBUG = True

    DRIVER = _pick_driver()                      
    SERVER = config("SQL_SERVER")
    DATABASE = config("SQL_DATABASE_QAS")
    USERNAME = config("SQL_USERNAME")
    PASSWORD = config("SQL_PASSWORD")

    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://{USERNAME}:{quote_plus(PASSWORD)}@{SERVER}/{DATABASE}"
        f"?driver={quote_plus(DRIVER)}&Encrypt=yes&TrustServerCertificate=yes"
    )

class ProductionConfig(Config):
    DEBUG = False

    DRIVER = _pick_driver()
    SERVER = config("SQL_SERVER")
    DATABASE = config("SQL_DATABASE_PROD")
    USERNAME = config("SQL_USERNAME")
    PASSWORD = config("SQL_PASSWORD")

    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://{USERNAME}:{quote_plus(PASSWORD)}@{SERVER}/{DATABASE}"
        f"?driver={quote_plus(DRIVER)}&Encrypt=yes&TrustServerCertificate=yes"
    )

def get_config(name: str | None):
    name = (name or config("FLASK_ENV") or "dev").lower()
    return {"dev": DevelopmentConfig, "prod": ProductionConfig}.get(name, DevelopmentConfig)
