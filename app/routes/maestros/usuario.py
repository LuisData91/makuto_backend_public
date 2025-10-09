from flask import Blueprint, jsonify
from marshmallow import ValidationError
from sqlalchemy import or_

from app.models.maestros.md_usuarios import Usuario
from app.schemas.maestros.usuarioDTO import UsuarioResponseDTO

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuario')

usuario_response_general = UsuarioResponseDTO()

@usuarios_bp.route("/", methods=['GET'])
def general():
    try:

        usuarios = Usuario.query.filter(Usuario.usr_del == '').order_by(Usuario.usr_cod.asc()).all()

        resultado = []
        for reg in usuarios:
            resultado.append({
                "usr_cod": reg.usr_cod,
                "usr_usu": reg.usr_usu,
                "usr_nom": reg.usr_nom,
                "usr_id": reg.usr_id
            })

        return jsonify({"usuarios": resultado}), 200
    
    except ValidationError as err:
        return jsonify({"error": "Error al listar usuarios", "detalle": str(err)}), 500
    

@usuarios_bp.route("/<user>", methods=['GET'])
def detalle(user):
    try:

        usuario = Usuario.query.filter(Usuario.usr_usu == user, Usuario.usr_del == '').first()

        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404

        resultado = {
            "usr_cod": usuario.usr_cod,
            "usr_usu": usuario.usr_usu,
            "usr_nom": usuario.usr_nom,
            "usr_id": usuario.usr_id
        }

        return jsonify({"usuario": resultado}), 200

    except Exception as err:
        return jsonify({"error": "Error al obtener usuario", "detalle": str(err)}), 500