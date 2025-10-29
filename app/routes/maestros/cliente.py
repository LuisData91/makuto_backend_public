from flask import Blueprint, request
from sqlalchemy import or_
from app.models.maestros.md_cliente import ClienteModel
from app.schemas.maestros.clienteDTO import ClienteResponseDTO
from app.extensions import db

cliente_bp = Blueprint('cliente', __name__, url_prefix='/cliente')

cliente_output_schema = ClienteResponseDTO()
cliente_output_lista_schema = ClienteResponseDTO(many=True)
SEDE='01'

@cliente_bp.get("")
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

        query = ClienteModel.query.filter(
            ClienteModel.delete == "",
            ClienteModel.estado == "2",
            ClienteModel.loja== SEDE
        )

        # Búsqueda
        if q:
            like = f"%{q}%"
            query = query.filter(or_(
                ClienteModel.cod.like(like),
                ClienteModel.nombre.like(like),
            ))
        else:
            if codigo:
                query = query.filter(ClienteModel.cod.like(f"%{codigo}%"))
            if nombre:
                query = query.filter(ClienteModel.nombre.like(f"%{nombre}%"))

        # Orden por nombre
        query = query.order_by(ClienteModel.nombre.asc())

        # Paginación
        try:
            paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        except AttributeError:
            paginated = db.paginate(query, page=page, per_page=per_page, error_out=False)

        data = cliente_output_lista_schema.dump(paginated.items)

        return {
            "message": "Lista de Clientes",
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

@cliente_bp.get("/<int:idCliente>")
def registro(idCliente: int):
    try:
        cliente = ClienteModel.query.filter(
            ClienteModel.delete == "",
            ClienteModel.cli_id == idCliente,
            ClienteModel.loja== SEDE
        ).first()

    except Exception as e:
        return {"message": "Ocurrió un error inesperado", "content": str(e)}, 500

    if cliente is None:
        return {"message": "Cliente no encontrado", "content": None}, 404

    return {
        "message": "Cliente encontrado",
        "content": cliente_output_schema.dump(cliente)
    }, 200

@cliente_bp.get("/loja")
def listar_cli_loja():
    try:
        # Parámetros de búsqueda
        q = (request.args.get("q") or "").strip()
        codigo = (request.args.get("codigo") or "").strip()
        nombre = (request.args.get("nombre") or "").strip()

        # Paginación segura
        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("per_page", default=20, type=int)
        per_page = min(max(per_page, 1), 100)

        # Query base
        query = ClienteModel.query.filter(
            or_(ClienteModel.delete == "", ClienteModel.delete.is_(None)),
            ClienteModel.estado.in_(("2", 2, "0"))  # puedes ajustar según tu lógica
        )

        # Búsqueda flexible
        if q:
            like = f"%{q}%"
            query = query.filter(or_(
                ClienteModel.cod.ilike(like),
                ClienteModel.nombre.ilike(like),
            ))
        else:
            if codigo:
                query = query.filter(ClienteModel.cod.ilike(f"%{codigo}%"))
            if nombre:
                query = query.filter(ClienteModel.nombre.ilike(f"%{nombre}%"))

        # Orden por nombre
        query = query.order_by(ClienteModel.nombre.asc())

        # Paginación (compatible con versiones nuevas y viejas)
        try:
            paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        except AttributeError:
            paginated = db.paginate(query, page=page, per_page=per_page, error_out=False)

        # Construir respuesta personalizada
        data = []
        for c in paginated.items:
            direccion_completa = " - ".join(
                s.strip() for s in [c.estado or "", c.distrito or "", c.direccion or ""] if s.strip()
            )

            data.append({
                "cli_id": c.cli_id,
                "codigo": c.cod.strip() if c.cod else "",
                "nombre": c.nombre.strip() if c.nombre else "",
                "telefono": c.telefono.strip() if c.telefono else "",
                "email": c.email.strip() if c.email else "",
                "direccion_completa": direccion_completa
            })


        return {
            "message": "Lista de Clientes",
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
