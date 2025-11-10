from flask import Blueprint, jsonify,current_app
from marshmallow import ValidationError
from sqlalchemy import or_,func

from app.models.maestros.md_usuarios import Usuario
from app.schemas.maestros.usuarioDTO import UsuarioResponseDTO

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuario')

usuario_response_general = UsuarioResponseDTO()

# Helper para "no borrado" en Protheus
def filtro_no_borrado():
    return or_(
        Usuario.usr_del == '',
        Usuario.usr_del == ' ',
        Usuario.usr_del.is_(None)
    )

# Helper para "no borrado" en Protheus
def filtro_no_borrado():
    return or_(
        Usuario.usr_del == '',
        Usuario.usr_del == ' ',
        Usuario.usr_del.is_(None)
    )

@usuarios_bp.route("/", methods=['GET'])
def general():
    try:
        usuarios = (
            Usuario.query
            .filter(filtro_no_borrado())
            .order_by(Usuario.usr_cod.asc())
            .all()
        )

        resultado = [{
            "usr_cod": u.usr_cod.strip() if isinstance(u.usr_cod, str) else u.usr_cod,
            "usr_usu": u.usr_usu.strip() if isinstance(u.usr_usu, str) else u.usr_usu,
            "usr_nom": u.usr_nom.strip() if isinstance(u.usr_nom, str) else u.usr_nom,
            "usr_id":  u.usr_id
        } for u in usuarios]

        return jsonify({"usuarios": resultado}), 200

    except Exception as err:
        current_app.logger.exception("Error al listar usuarios")
        return jsonify({"message": "Error al listar usuarios", "detail": str(err)}), 500


@usuarios_bp.route("/<user>", methods=['GET'])
def detalle(user):
    try:
        user = (user or "").strip()

        usuario = (
            Usuario.query
            .filter(
                filtro_no_borrado(),
                func.trim(Usuario.usr_usu) == user  # o .ilike(user) si quieres case-insensitive
            )
            .first()
        )

        if not usuario:
            return jsonify({"message": "Usuario no encontrado", "codigo": user}), 404

        resultado = {
            "usr_cod": usuario.usr_cod.strip() if isinstance(usuario.usr_cod, str) else usuario.usr_cod,
            "usr_usu": usuario.usr_usu.strip() if isinstance(usuario.usr_usu, str) else usuario.usr_usu,
            "usr_nom": usuario.usr_nom.strip() if isinstance(usuario.usr_nom, str) else usuario.usr_nom,
            "usr_id":  usuario.usr_id
        }

        return jsonify({"usuario": resultado}), 200

    except Exception as err:
        current_app.logger.exception("Error al obtener usuario %s", user)
        return jsonify({"message": "Error al obtener usuario", "detail": str(err)}), 500


