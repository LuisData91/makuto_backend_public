# controllers/solicitud_reclamo_controller.py
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError
from sqlalchemy import func
from datetime import datetime
from app.extensions import db

# Rutas de modelos/DTOs según tu estructura
from app.models.transacciones.md_SolicitudReclamo import SolicitudReclamoModel
from app.schemas.maestros.SolicitudReclamoDTO import (
    SolicitudReclamoResponseDTO,
    ReclamoCreateRequestDTO,
    ReclamoUpdateRequestDTO,
)

solicitud_reclamo_bp = Blueprint("solicitud_reclamo_bp", __name__, url_prefix="/api/reclamos")

# Schemas reutilizables
resp_schema = SolicitudReclamoResponseDTO()
resp_list_schema = SolicitudReclamoResponseDTO(many=True)
create_schema = ReclamoCreateRequestDTO()
update_schema = ReclamoUpdateRequestDTO()

# -------------------- Crear --------------------
@solicitud_reclamo_bp.post("")
def crear_reclamo():
    try:
        payload = create_schema.load(request.get_json(silent=True) or {})
        nuevo = SolicitudReclamoModel(**payload)  # estado por defecto = 1 en el modelo
        db.session.add(nuevo)
        db.session.commit()
        return jsonify(resp_schema.dump(nuevo)), 201
    except ValidationError as ve:
        return jsonify({"message": "Datos inválidos", "errors": ve.messages}), 400
    except IntegrityError as ie:
        db.session.rollback()
        return jsonify({"message": "Error de integridad", "detail": str(ie.orig)}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al crear reclamo", "detail": str(e)}), 500

# -------------------- Actualizar (PUT/PATCH) --------------------
@solicitud_reclamo_bp.put("/<int:id>")
@solicitud_reclamo_bp.patch("/<int:id>")
def actualizar_reclamo(id: int):
    try:
        cambios = update_schema.load(request.get_json(silent=True) or {})
        reclamo = SolicitudReclamoModel.query.get(id)
        if not reclamo or reclamo.estado == 0:
            return jsonify({"message": "Reclamo no encontrado"}), 404

        for k, v in cambios.items():
            setattr(reclamo, k, v)

        # marca de actualización (si tu modelo ya tiene server_default, igual sirve forzar aquí)
        reclamo.fecha_mod = datetime.now().strftime("%Y%m%d")
        db.session.commit()
        return jsonify(resp_schema.dump(reclamo)), 200
    except ValidationError as ve:
        return jsonify({"message": "Datos inválidos", "errors": ve.messages}), 400
    except IntegrityError as ie:
        db.session.rollback()
        return jsonify({"message": "Error de integridad", "detail": str(ie.orig)}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al actualizar reclamo", "detail": str(e)}), 500

# -------------------- “Eliminar” (Soft Delete -> estado = 0) --------------------
@solicitud_reclamo_bp.delete("/<int:id>")
def eliminar_reclamo(id: int):
    try:
        reclamo = SolicitudReclamoModel.query.get(id)
        if not reclamo or reclamo.estado == 0:
            return jsonify({"message": "Reclamo no encontrado"}), 404

        reclamo.estado = 0
        reclamo.fecha_mod = func.current_timestamp()
        db.session.commit()
        return jsonify({"message": "Reclamo deshabilitado (estado=0)"}), 200
    except IntegrityError as ie:
        db.session.rollback()
        return jsonify({"message": "Error de integridad", "detail": str(ie.orig)}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al deshabilitar reclamo", "detail": str(e)}), 500

# -------------------- Listar activos --------------------
@solicitud_reclamo_bp.get("")
def listar_reclamos():
    qs = (
        SolicitudReclamoModel.query
        .filter(SolicitudReclamoModel.estado == 1)
        .order_by(SolicitudReclamoModel.id.desc())
    )
    return jsonify(resp_list_schema.dump(qs.all())), 200

# --------------------- Obtener por num_doc (documento) --------------------
@solicitud_reclamo_bp.get("/<string:num_doc>")
def obtener_reclamo(num_doc: str):
    # Buscar por campo NUM_DOC (documento) y que esté activo
    r = SolicitudReclamoModel.query.filter_by(documento=num_doc, estado=1).first()

    if not r:
        return jsonify({"message": f"Reclamo con documento {num_doc} no encontrado"}), 404

    return jsonify(resp_schema.dump(r)), 200

