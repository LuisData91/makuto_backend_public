

# app/__init__.py
import os   
from flask import Flask
from flask_cors import CORS
from .config import get_config
from dotenv import load_dotenv
# from .extensions import db ,validador , jwt 
from app.extensions import db, validador, jwt


def create_app(config_name: str | None = None) -> Flask:
   
    load_dotenv()

    app = Flask(__name__)
    cfg = get_config(config_name)
    app.config.from_object(cfg)
    CORS(app)


    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

  
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET", "dev-jwt-secret")

    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_HEADER_NAME"] = "Authorization"
    app.config["JWT_HEADER_TYPE"] = "Bearer"


    app.config["JWT_COOKIE_CSRF_PROTECT"] = False



    # Inicializa extensiones
    db.init_app(app)
    validador.init_app(app)
    jwt.init_app(app)

    @app.get("/")
    def welcome():
        return {"status": "ok", "app": "Bienvenido al API MAkuto"}, 200

    # IMPORTA Y REGISTRA BLUEPRINTS *DESPUÉS* de init_app
    from app.routes.maestros.cliente import cliente_bp
    from app.routes.maestros.familia import familia_bp
    from app.routes.maestros.producto import producto_bp
    from app.routes.maestros.tecnico import tecnico_bp
    from app.routes.maestros.vendedor import vendedor_bp
    from app.routes.maestros.visita import visita_bp 
    from app.routes.maestros.form_visita import bp_visitas
    from app.routes.maestros.usuario import usuarios_bp
    from app.routes.maestros.empleados import empleado_bp
    from app.routes.maestros.proxy import proxy_bp
    from app.routes.maestros.SolicitudReclamo import solicitud_reclamo_bp
    from app.routes.maestros.Adjunto import adjuntos_bp

    app.register_blueprint(cliente_bp)
    app.register_blueprint(familia_bp)
    app.register_blueprint(producto_bp)
    app.register_blueprint(tecnico_bp)
    app.register_blueprint(vendedor_bp)
    app.register_blueprint(visita_bp)
    app.register_blueprint(bp_visitas)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(empleado_bp)
    app.register_blueprint(proxy_bp, url_prefix="/api")
    app.register_blueprint(solicitud_reclamo_bp)
    app.register_blueprint(adjuntos_bp)

   



    return app
