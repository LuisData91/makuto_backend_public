from flask import Blueprint, request
from sqlalchemy import or_
from app.models.maestros.md_visita import TipoVisitaModel
from app.schemas.maestros.visitaDTO import VisitaResponseDTO
from app.extensions import db

visita_bp = Blueprint('visita', __name__, url_prefix='/visita')

visita_output_schema = VisitaResponseDTO()
visita_output_lista_schema = VisitaResponseDTO(many=True)

@visita_bp.get("")
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

        query = TipoVisitaModel.query.filter(
                
        )

        # Búsqueda
        if q:
            like = f"%{q}%"
            query = query.filter(or_(
                TipoVisitaModel.id_visita.like(like),
                TipoVisitaModel.descripcion.like(like),
            ))
        else:
            if codigo:
                query = query.filter(TipoVisitaModel.id_visita.like(f"%{codigo}%"))
            if nombre:
                query = query.filter(TipoVisitaModel.descripcion.like(f"%{nombre}%"))

        # Orden por nombre
        query = query.order_by(TipoVisitaModel.descripcion.asc())

        # Paginación
        try:
            paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        except AttributeError:
            paginated = db.paginate(query, page=page, per_page=per_page, error_out=False)

        data = visita_output_lista_schema.dump(paginated.items)

        return {
            "message": "Lista de Visitas",
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

@visita_bp.get("/<int:idVisita>")
def registro(idVisita: int):
    try:
        visita = TipoVisitaModel.query.filter(
            
            TipoVisitaModel.id_visita == idVisita
        ).first()

    except Exception as e:
        return {"message": "Ocurrió un error inesperado", "content": str(e)}, 500

    if visita is None:
        return {"message": "Tecnico no encontrado", "content": None}, 404

    return {
        "message": "Tecnico encontrado",
        "content": visita_output_schema.dump(visita)
    }, 200