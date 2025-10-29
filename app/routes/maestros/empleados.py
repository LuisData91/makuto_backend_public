from flask import Blueprint, request
from sqlalchemy import or_
from app.models.maestros.md_empleado import EmpleadoModel
from app.schemas.maestros.empleadoDTO import EmpleadoResponseDTO
from app.extensions import db


empleado_bp = Blueprint('empleado', __name__, url_prefix='/empleado')

empleadp_output_schema = EmpleadoResponseDTO()
empleado_output_lista_schema = EmpleadoResponseDTO(many=True)


@empleado_bp.get("")
def general():
    try:
        # Parámetros de búsqueda
        q = (request.args.get("q") or "").strip()
        dni = (request.args.get("dni") or "").strip()
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

        query = EmpleadoModel.query.filter(
            EmpleadoModel.delete == "",
            EmpleadoModel.f_baja == ""
        )

        # Búsqueda
        if q:
            like = f"%{q}%"
            query = query.filter(or_(
                EmpleadoModel.empleado_id.like(like),
                EmpleadoModel.nombres.like(like),
                EmpleadoModel.dni.like(like),
            ))
        else:
            if dni:
                query = query.filter(EmpleadoModel.dni.like(f"%{dni}%"))
            if nombre:
                query = query.filter(EmpleadoModel.nombres.like(f"%{nombre}%"))

        # Orden por nombre
        query = query.order_by(EmpleadoModel.nombres.asc())

        # Paginación
        try:
            paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        except AttributeError:
            paginated = db.paginate(query, page=page, per_page=per_page, error_out=False)

        data = empleado_output_lista_schema.dump(paginated.items)

        return {
            "message": "Lista de Empleados",
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
        return {"message": "Ocurrió un error inesperado carga empleado", "content": str(e)}, 500

@empleado_bp.get("/<string:idEmpleado>")
def get_empleado(idEmpleado):    
    try:
        empleado = EmpleadoModel.query.filter(
            EmpleadoModel.delete == "",
            EmpleadoModel.empleado_id == idEmpleado,
            EmpleadoModel.f_baja == ""
        ).first()

    except Exception as e:
        return {"message": "Ocurrió un error inesperado al obtener empleado", "content": str(e)}, 500

    if not empleado:
        return {"message": "Empleado no encontrado", "content": {}}, 404

    data = empleadp_output_schema.dump(empleado)

    return {"message": "Detalle de Empleado", "content": data}, 200
