from flask import Flask
from .config import get_config
from .extensions import db

# Lista de Rutas
from app.routes.maestros.cliente import cliente_bp
from app.routes.maestros.familia import familia_bp
from app.routes.maestros.producto import producto_bp
from app.routes.maestros.tecnico import tecnico_bp

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
    app.register_blueprint(cliente_bp)
    app.register_blueprint(familia_bp)
    app.register_blueprint(producto_bp)
    app.register_blueprint(tecnico_bp)
    
    return app