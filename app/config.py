from decouple import config
from urllib.parse import quote_plus
from datetime import timedelta

# Configuración General
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

# Ambiente de Desarrollo
class DevelopmentConfig(Config):
    DEBUG = True

    DRIVER = config("SQL_DRIVER", default="ODBC Driver 18 for SQL Server")
    SERVER = config("SQL_SERVER")
    DATABASE = config("SQL_DATABASE_QAS")
    USERNAME = config("SQL_USERNAME")
    PASSWORD = config("SQL_PASSWORD")

    PASSWORD_ENCODED = quote_plus(PASSWORD)

    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://{USERNAME}:{PASSWORD_ENCODED}@{SERVER}/{DATABASE}"
        f"?driver={DRIVER}&Encrypt=yes&TrustServerCertificate=yes"
    )

# Ambiente de Producción
class ProductionConfig(Config):
    DEBUG = False

    DRIVER = config("SQL_DRIVER", default="ODBC Driver 18 for SQL Server")
    SERVER = config("SQL_SERVER")
    DATABASE = config("SQL_DATABASE_PROD")
    USERNAME = config("SQL_USERNAME")
    PASSWORD = config("SQL_PASSWORD")

    PASSWORD_ENCODED = quote_plus(PASSWORD)

    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://{USERNAME}:{PASSWORD_ENCODED}@{SERVER}/{DATABASE}"
        f"?driver={DRIVER}&Encrypt=yes&TrustServerCertificate=yes"
    )

def get_config(name: str | None):
    name = (name or config("FLASK_ENV") or "dev").lower()
    return {
        "dev": DevelopmentConfig,
        "prod": ProductionConfig,
    }.get(name, DevelopmentConfig)