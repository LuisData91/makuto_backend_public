from flask import Blueprint, request,jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from marshmallow import ValidationError
from datetime import datetime, timezone
from app.models.maestros.md_tecnicos import TecnicosModel
from app.schemas.maestros.tecnicoDTO import TecnicoResponseDTO, TecnicoCreateRequestDTO,TecnicoUpdateRequestDTO
from app.extensions import db

tecnico_bp = Blueprint('tecnico', __name__, url_prefix='/tecnico')

tecnico_output_schema = TecnicoResponseDTO()
tecnico_output_lista_schema = TecnicoResponseDTO(many=True)
tecnico_create_schema = TecnicoCreateRequestDTO()
tecnico_update_schema = TecnicoUpdateRequestDTO()

@tecnico_bp.get("")
def general():
    try:
        # Parámetros de búsqueda
        q = (request.args.get("q") or "").strip()
        codigo = (request.args.get("codigo") or "").strip()
        nombre = (request.args.get("nombre") or "").strip()

        # Paginación
        try:
            page = max(1, int(request.args.get("page", 1)))
        except ValueError:
            page = 1
        try:
            per_page = min(max(1, int(request.args.get("per_page", 20))), 100)
        except ValueError:
            per_page = 20

        query = TecnicosModel.query.filter(
                TecnicosModel.estado == "1"
        )

        # Búsqueda
        if q:
            like = f"%{q}%"
            query = query.filter(or_(
                TecnicosModel.cod_tec.like(like),
                TecnicosModel.nombre.like(like),
            ))
        else:
            if codigo:
                query = query.filter(TecnicosModel.cod_tec.like(f"%{codigo}%"))
            if nombre:
                query = query.filter(TecnicosModel.nombre.like(f"%{nombre}%"))

        # Orden por nombre
        query = query.order_by(TecnicosModel.nombre.asc())

        # Paginación
        try:
            paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        except AttributeError:
            paginated = db.paginate(query, page=page, per_page=per_page, error_out=False)

        data = tecnico_output_lista_schema.dump(paginated.items)

        return {
            "message": "Lista de Tecnicos",
            "content": data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": paginated.total,
                "pages": paginated.pages,
                "has_next": paginated.has_next,
                "has_prev": paginated.has_prev
            }
        }, 200
    
    except Exception as e:
        return {"message": "Ocurrió un error inesperado", "content": str(e)}, 500

@tecnico_bp.get("/<string:idTecnico>")
def registro(idTecnico: str):
    try:
        tecnico = TecnicosModel.query.filter(
            
            TecnicosModel.cod_tec == idTecnico
        ).first()

    except Exception as e:
        return {"message": "Ocurrió un error inesperado", "content": str(e)}, 500

    if tecnico is None:
        return {"message": "Tecnico no encontrado", "content": None}, 404

    return {
        "message": "Tecnico encontrado",
        "content": tecnico_output_schema.dump(tecnico)
    }, 200

    # RUTA PARA AGREGAR REGISTRO
@tecnico_bp.post("")
def crear():
        
        if not request.is_json:
            return jsonify({
                "message": "El cuerpo de la solicitud debe ser JSON.",
                "content": []
            }), 400

        json_data = request.get_json(silent=True) or {}

        try:
            tecnico = tecnico_create_schema.load(json_data)
            db.session.add(tecnico)
            
            db.session.commit()

            result = tecnico_output_schema.dump(tecnico)
            return {
                "message": "Técnico creada satisfactoriamente",
                "content": result
            }, 201

        except ValidationError as err:
            db.session.rollback()
            return {"message": "Algunos datos son incorrectos", "content": err.messages}, 400

        except IntegrityError as err:
            db.session.rollback()

            msg = "Violación de unicidad en base de datos."
            # (Opcional) extrae info de MySQL: err.orig.args si necesitas el código
            return {"message": "Algunos datos son incorrectos", "content": {"_schema": [msg]}}, 400

        except Exception:
            db.session.rollback()
  
            return {"message": "Ocurrió un error inesperado", "content": []}, 500
        
# -------ACTUALIZAR REGISTRO-------
@tecnico_bp.route("/<string:tec_id>", methods=["PUT"])
def modificar(tec_id: str):
    try:
        # Buscar el registro
        tecnico = (
            db.session.query(TecnicosModel)
            .filter(TecnicosModel.cod_tec == tec_id)
            .first()
        )
    except Exception as e:
        return {"message": "Ocurrió un error inesperado", "content": str(e)}, 500

    if not tecnico:
        return {"message": "tecnico no encontrada", "content": []}, 404

    if not request.is_json:
        return jsonify({
            "message": "El cuerpo de la solicitud debe ser JSON.",
            "content": []
        }), 400

    json_data = request.get_json(silent=True) or {}

    try:
        # Validar payload
        try:
            data = tecnico_update_schema.load(json_data, partial=False)
        except ValidationError as err:
            return jsonify({"message": "Algunos datos son incorrectos", "content": err.messages}), 400

        # Aplicar cambios
        for field, value in data.items():
            setattr(tecnico, field, value)

        db.session.add(tecnico)
        db.session.commit()

        # Serializar estado final
        datos_nuevos = tecnico_output_schema.dump(tecnico)

        return {
            "message": "Técnico actualizada satisfactoriamente",
            "content": datos_nuevos
        }, 200

    except ValidationError as err:
        db.session.rollback()
        return jsonify({
            "message": "Algunos datos son incorrectos",
            "content": err.messages
        }), 400

    except IntegrityError:
        db.session.rollback()
        msg = "Violación de unicidad en base de datos."
        return jsonify({
            "message": "Algunos datos son incorrectos",
            "content": {"_schema": [msg]}
        }), 400

    except Exception as e:
        db.session.rollback()
        return {"message": "Ocurrió un error inesperado", "content": str(e)}, 500
