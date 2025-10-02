from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError
from datetime import datetime, timezone
from decimal import Decimal

from app.extensions import db
from app.models.transacciones.md_cabRegIT import cabRegITModel
from app.models.transacciones.md_det import detModel
from app.schemas.maestros.form_visitaDTO import cabRegITCreateRequestDTO, cabRegITUpdateRequestDTO,cabRegITResponseDTO,detCreateRequestDTO,detUpdateRequestDTO,detResponseDTO
form_visita_bp = Blueprint('form_visita', __name__, url_prefix='/form_visita')
cabRegIT_output_schema = cabRegITResponseDTO()
cabRegIT_output_lista_schema = cabRegITResponseDTO(many=True)
cabRegIT_create_schema = cabRegITCreateRequestDTO()
cabRegIT_update_schema = cabRegITUpdateRequestDTO()

det_output_schema = detResponseDTO()
det_output_lista_schema = detResponseDTO(many=True) 
det_create_schema = detCreateRequestDTO()
det_update_schema = detUpdateRequestDTO()

# -------- CABECERA --------
@form_visita_bp.route("/cab", methods=["POST"])
def crear_cab():
    if not request.is_json:
        return jsonify({"message": "El cuerpo de la solicitud debe ser JSON.", "content": []}), 400
    try:
        payload = request.get_json(silent=False)
    except Exception:
        return jsonify({"message": "JSON mal formado.", "content": []}), 400

    try:
        cab = cabRegIT_create_schema.load(payload)  # gracias a @post_load devuelve cabRegITModel
        db.session.add(cab)
        db.session.commit()
        return {
            "message": "Cabecera creada satisfactoriamente",
            "content": cabRegIT_output_schema.dump(cab)
        }, 201

    except ValidationError as err:
        db.session.rollback()
        return {"message": "Algunos datos son incorrectos", "content": err.messages}, 400

    except IntegrityError:
        db.session.rollback()
        return {"message": "Algunos datos son incorrectos", "content": {"_schema": ["Violación de unicidad en base de datos."]}}, 400

    except Exception as e:
        db.session.rollback()
        return {"message": "Ocurrió un error inesperado", "content": str(e)}, 500


@form_visita_bp.route("/cab", methods=["GET"])
def listar_cab():
    rows = cabRegITModel.query.order_by(cabRegITModel.id.desc()).all()
    return {"message": "OK", "content": cabRegIT_output_lista_schema.dump(rows)}, 200


@form_visita_bp.route("/cab/<int:cab_id>", methods=["PUT"])
def actualizar_cab(cab_id: int):
    cab = db.session.get(cabRegITModel, cab_id)
    if not cab:
        return {"message": "Cabecera no encontrada", "content": []}, 404

    if not request.is_json:
        return jsonify({"message": "El cuerpo de la solicitud debe ser JSON.", "content": []}), 400

    try:
        payload = request.get_json(silent=False)
    except Exception:
        return jsonify({"message": "JSON mal formado.", "content": []}), 400

    try:
        data = cabRegIT_update_schema.load(payload, partial=True)  # permite actualizar parcialmente
        for k, v in data.items():
            setattr(cab, k, v)

        db.session.commit()
        return {"message": "Cabecera actualizada satisfactoriamente", "content": cabRegIT_output_schema.dump(cab)}, 200

    except ValidationError as err:
        db.session.rollback()
        return {"message": "Algunos datos son incorrectos", "content": err.messages}, 400

    except IntegrityError:
        db.session.rollback()
        return {"message": "Algunos datos son incorrectos", "content": {"_schema": ["Violación de unicidad en base de datos."]}}, 400

    except Exception as e:
        db.session.rollback()
        return {"message": "Ocurrió un error inesperado", "content": str(e)}, 500

# -------- DETALLE --------
@form_visita_bp.route("/det", methods=["POST"])
def crear_det():
    if not request.is_json:
        return jsonify({"message": "El cuerpo de la solicitud debe ser JSON.", "content": []}), 400
    try:
        payload = request.get_json(silent=False)
    except Exception:
        return jsonify({"message": "JSON mal formado.", "content": []}), 400

    try:
        det = det_create_schema.load(payload)  # detModel gracias a @post_load
        # Verificar que la cabecera exista
        cab = db.session.get(cabRegITModel, det.id_cab)
        if not cab:
            return {"message": "Cabecera (id_cab) no existe", "content": []}, 404

        db.session.add(det)
        db.session.commit()
        return {"message": "Detalle creado satisfactoriamente", "content": det_output_schema.dump(det)}, 201

    except ValidationError as err:
        db.session.rollback()
        return {"message": "Algunos datos son incorrectos", "content": err.messages}, 400

    except IntegrityError:
        db.session.rollback()
        return {"message": "Algunos datos son incorrectos", "content": {"_schema": ["Violación de unicidad en base de datos."]}}, 400

    except Exception as e:
        db.session.rollback()
        return {"message": "Ocurrió un error inesperado", "content": str(e)}, 500


@form_visita_bp.route("/cab/<int:cab_id>/det", methods=["GET"])
def listar_det_por_cab(cab_id: int):
    # Opcional: 404 si la cabecera no existe
    detalles = detModel.query.filter_by(id_cab=cab_id).all()
    return {"message": "OK", "content": det_output_lista_schema.dump(detalles)}, 200


@form_visita_bp.route("/det/<int:det_id>", methods=["PUT"])
def actualizar_det(det_id: int):
    det = db.session.get(detModel, det_id)
    if not det:
        return {"message": "Detalle no encontrado", "content": []}, 404

    if not request.is_json:
        return jsonify({"message": "El cuerpo de la solicitud debe ser JSON.", "content": []}), 400

    try:
        payload = request.get_json(silent=False)
    except Exception:
        return jsonify({"message": "JSON mal formado.", "content": []}), 400

    try:
        data = det_update_schema.load(payload, partial=True)
        # Si cambia id_cab, valida que exista la nueva cabecera
        if "id_cab" in data:
            if not db.session.get(cabRegITModel, data["id_cab"]):
                return {"message": "Cabecera (id_cab) no existe", "content": []}, 404

        for k, v in data.items():
            setattr(det, k, v)

        db.session.commit()
        return {"message": "Detalle actualizado satisfactoriamente", "content": det_output_schema.dump(det)}, 200

    except ValidationError as err:
        db.session.rollback()
        return {"message": "Algunos datos son incorrectos", "content": err.messages}, 400

    except IntegrityError:
        db.session.rollback()
        return {"message": "Algunos datos son incorrectos", "content": {"_schema": ["Violación de unicidad en base de datos."]}}, 400

    except Exception as e:
        db.session.rollback()
        return {"message": "Ocurrió un error inesperado", "content": str(e)}, 500