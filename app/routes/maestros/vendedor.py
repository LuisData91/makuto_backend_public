from flask import Blueprint, request
from sqlalchemy import or_
from app.models.maestros.md_vendedor import VendedorModel
from app.schemas.maestros.vendedorDTO import VendedorResponseDTO
from app.extensions import db

vendedor_bp = Blueprint('vendedor', __name__, url_prefix='/vendedor')

vendedor_output_schema = VendedorResponseDTO()
vendedor_output_lista_schema = VendedorResponseDTO(many=True)
GRUPOS_PERMITIDOS = ['LA','LM','LV','LS','IC','HY','HU','AQ','CU','JU','TR','CH','PI']

@vendedor_bp.get("")
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

        query = VendedorModel.query.filter(
            VendedorModel.delete == "",
            VendedorModel.estado == "2",
            VendedorModel.grupo.in_(GRUPOS_PERMITIDOS)
        )

        # Búsqueda
        if q:
            like = f"%{q}%"
            query = query.filter(or_(
                VendedorModel.cod.like(like),
                VendedorModel.nombre.like(like),
            ))
        else:
            if codigo:
                query = query.filter(VendedorModel.cod.like(f"%{codigo}%"))
            if nombre:
                query = query.filter(VendedorModel.nombre.like(f"%{nombre}%"))

        # Orden por nombre
        query = query.order_by(VendedorModel.nombre.asc())
        

        # Paginación
        try:
            paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        except AttributeError:
            paginated = db.paginate(query, page=page, per_page=per_page, error_out=False)

        data =vendedor_output_lista_schema.dump(paginated.items)

        return {
            "message": "Lista de Vendedores",
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

@vendedor_bp.get("/<string:idVendedor>")
def registro(idVendedor: str):
    try:
        vendedor = VendedorModel.query.filter(
            VendedorModel.delete == "",
            VendedorModel.cod == idVendedor,
            VendedorModel.grupo.in_(GRUPOS_PERMITIDOS)

        ).first()

    except Exception as e:
        return {"message": "Ocurrió un error inesperado", "content": str(e)}, 500

    if vendedor is None:
        return {"message": "Vendedor no encontrado", "content": None}, 404

    return {
        "message": "Vendedor encontrado",
        "content": vendedor_output_schema.dump(vendedor)
    }, 200