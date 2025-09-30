from flask import Flask
from .config import get_config
from .extensions import db

# Lista de Rutas

def create_app(config_name: str | None=None)-> Flask:
    app = Flask(__name__)
    cfg = get_config(config_name)
    app.config.from_object(cfg)

    # Extensiones
    db.init_app(app)

    @app.get("/")
    def welcome():
        return{
            "status": "ok",
            "app": "Bienvenido al API MAkuto"
        }, 200
    
    # Lista de Blueprint
    
    return app