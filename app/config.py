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
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1, minutes=30)
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer" 

# Ambiente de Desarrollo
class DevelopmentConfig(Config):
    DEBUG = True

    # SERVER = config("SQL_SERVER")
    # DATABASE = config("SQL_DATABASE_QAS")
    # USERNAME = config("SQL_USERNAME")
    # PASSWORD = quote_plus(config("SQL_PASSWORD"))

    # SQLALCHEMY_DATABASE_URI = (
    #     f"mysql+pymysql://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}?charset=utf8mb4"
    # )

# Ambiente de Producción
class ProductionConfig(Config):
    DEBUG = False

    # SERVER = config("SQL_SERVER")
    # DATABASE = config("SQL_DATABASE_PROD")
    # USERNAME = config("SQL_USERNAME")
    # PASSWORD = quote_plus(config("SQL_PASSWORD"))

    # SQLALCHEMY_DATABASE_URI = (
    #     f"mysql+pymysql://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}?charset=utf8mb4"
    # )

def get_config(name: str | None):
    name = (name or config("FLASK_ENV") or "dev").lower()
    return {
        "dev": DevelopmentConfig,
        "prod": ProductionConfig,
    }.get(name, DevelopmentConfig)