from flask import Blueprint, request
from sqlalchemy import or_
from app.models.maestros.md_productos import ProductoModel
from app.schemas.maestros.productoDTO import ProductoResponseDTO
from app.extensions import db

producto_bp = Blueprint('producto', __name__, url_prefix='/producto')

producto_output_schema = ProductoResponseDTO()
producto_output_lista_schema = ProductoResponseDTO(many=True)
TipoProd=['ME','PT']

@producto_bp.get("")
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

        query = ProductoModel.query.filter(
            ProductoModel.delete == "",
            ProductoModel.estado == "2",
            ProductoModel.tipo.in_(TipoProd)
        )

        # Búsqueda
        if q:
            like = f"%{q}%"
            query = query.filter(or_(
                ProductoModel.cod.like(like),
                ProductoModel.nombre.like(like),
            ))
        else:
            if codigo:
                query = query.filter(ProductoModel.cod.like(f"%{codigo}%"))
            if nombre:
                query = query.filter(ProductoModel.nombre.like(f"%{nombre}%"))

        # Orden por nombre
        query = query.order_by(ProductoModel.nombre.asc())

        # Paginación
        try:
            paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        except AttributeError:
            paginated = db.paginate(query, page=page, per_page=per_page, error_out=False)

        data =producto_output_lista_schema.dump(paginated.items)

        return {
            "message": "Lista de Producto",
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

@producto_bp.get("/<string:idProducto>")
def registro(idProducto: str):
    try:
        producto = ProductoModel.query.filter(
            ProductoModel.delete == "",
            ProductoModel.cod == idProducto,
            ProductoModel.tipo.in_(TipoProd)
        ).first()

    except Exception as e:
        return {"message": "Ocurrió un error inesperado", "content": str(e)}, 500

    if producto is None:
        return {"message": "producto no encontrado", "content": None}, 404

    return {
        "message": "Producto encontrado",
        "content": producto_output_schema.dump(producto)
    }, 200