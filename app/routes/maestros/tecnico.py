from flask import Blueprint, request
from sqlalchemy import or_
from app.models.maestros.md_tecnicos import TecnicosModel
from app.schemas.maestros.tecnicoDTO import TecnicoResponseDTO
from app.extensions import db

tecnico_bp = Blueprint('tecnico', __name__, url_prefix='/tecnico')

tecnico_output_schema = TecnicoResponseDTO()
tecnico_output_lista_schema = TecnicoResponseDTO(many=True)

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