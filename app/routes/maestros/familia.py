from flask import Blueprint, request
from sqlalchemy import or_
from app.models.maestros.md_familia import FamiliaModel
from app.schemas.maestros.familiaDTO import FamiliaResponseDTO
from app.extensions import db


familia_bp = Blueprint('familia', __name__, url_prefix='/familia')

familia_output_schema = FamiliaResponseDTO()
familia_output_lista_schema = FamiliaResponseDTO(many=True)



@familia_bp.get("")
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

        query = FamiliaModel.query.filter(
            FamiliaModel.delete == "",
           
        )

        # Búsqueda
        if q:
            like = f"%{q}%"
            query = query.filter(or_(
                FamiliaModel.cod.like(like),
                FamiliaModel.descripcion.like(like),
            ))
        else:
            if codigo:
                query = query.filter(FamiliaModel.cod.like(f"%{codigo}%"))
            if nombre:
                query = query.filter(FamiliaModel.descripcion.like(f"%{nombre}%"))

        # Orden por nombre
        query = query.order_by(FamiliaModel.descripcion.asc())

        # Paginación
        try:
            paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        except AttributeError:
            paginated = db.paginate(query, page=page, per_page=per_page, error_out=False)

        data = familia_output_lista_schema.dump(paginated.items)

        return {
            "message": "Lista de Familia",
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
    


@familia_bp.get("/<int:idFamilia>")
def registro(idFamilia: int):
    try:
        cliente = FamiliaModel.query.filter(
            FamiliaModel.delete == "",
            FamiliaModel.cli_id == idFamilia
        ).first()

    except Exception as e:
        return {"message": "Ocurrió un error inesperado", "content": str(e)}, 500

    if cliente is None:
        return {"message": "Familia no encontrado", "content": None}, 404

    return {
        "message": "Familia encontrado",
        "content": familia_output_schema.dump(cliente)
    }, 200
