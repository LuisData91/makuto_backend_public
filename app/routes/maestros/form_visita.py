from sqlalchemy import func, and_
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import func ,literal_column, or_,and_
from sqlalchemy.orm import aliased
from app.extensions import db
from app.models.transacciones.md_cabRegIT import cabRegITModel
from app.models.transacciones.md_det import detModel
from marshmallow import ValidationError
from app.schemas.maestros.form_visitaDTO import (
    cabRegITCreateRequestDTO, cabRegITUpdateRequestDTO, cabRegITResponseDTO,
    detCreateRequestDTO, detUpdateRequestDTO, detResponseDTO
)
from app.models.maestros.md_cliente import ClienteModel   # SA1010
from app.models.maestros.md_vendedor import VendedorModel # SA3010
from app.models.maestros.md_visita import TipoVisitaModel     # BKS0088 (motivo)
from app.models.maestros.md_tecnicos import TecnicosModel 
from app.utils.correlativo import next_correlativo_mssql


bp_visitas = Blueprint("visitas", __name__, url_prefix="/api/visitas")

# ===== Helpers =====
def ok(data=None, status=200):
    return jsonify({"ok": True, "data": data}), status

def fail(message="Error interno", status=500):
    return jsonify({"ok": False, "message": message}), status

# ===== CABECERA =====

@bp_visitas.get("")
def list_visitas():
    """Listar visitas (con filtros simples)"""
    q = cabRegITModel.query
    estado = request.args.get("estado", type=int, default=1)
    if estado in (0, 1):
        q = q.filter(cabRegITModel.estado == estado)

    id_tec = request.args.get("id_tec")
    if id_tec:
        q = q.filter(cabRegITModel.id_tec == id_tec)

    id_vend = request.args.get("id_vend")
    if id_vend:
        q = q.filter(cabRegITModel.id_vend == id_vend)

    # paginación básica
    page = request.args.get("page", type=int, default=1)
    size = request.args.get("size", type=int, default=20)
    pag = q.order_by(cabRegITModel.id.desc()).paginate(page=page, per_page=size, error_out=False)

    dto = cabRegITResponseDTO(many=True)
    return ok({
        "items": dto.dump(pag.items),
        "page": pag.page,
        "pages": pag.pages,
        "total": pag.total
    })

@bp_visitas.get("/<int:idcab>")
def get_visita(idcab):
    cab = cabRegITModel.query.get_or_404(idcab)
    dto = cabRegITResponseDTO()
    # incluir detalles activos
    detalles = detModel.query.filter_by(id_cab=idcab, estado=1).all()
    det_dto = detResponseDTO(many=True)
    data = dto.dump(cab)
    data["detalles"] = det_dto.dump(detalles)
    return ok(data)

@bp_visitas.post("")
def create_visita():
    """
    Crea solo la CABECERA.
    Si quieres crear cabecera + detalles en una sola transacción, usa /api/visitas/full (abajo).
    """
    try:
        payload = request.get_json() or {}
        cab = cabRegITCreateRequestDTO().load(payload)  # -> cabRegITModel por @post_load
        db.session.add(cab)
        db.session.commit()
        return ok({"id": cab.id}, status=201)
    except IntegrityError as e:
        db.session.rollback()
        return fail(f"Integridad: {str(e.orig)}", 400)
    except SQLAlchemyError as e:
        db.session.rollback()
        return fail(str(e))

@bp_visitas.put("/<int:idcab>")
@bp_visitas.patch("/<int:idcab>")
def update_visita(idcab):
    try:
        cab = cabRegITModel.query.get_or_404(idcab)
        partial = request.method == "PATCH"  # <-- PATCH permite campos parciales
        data = cabRegITUpdateRequestDTO().load(request.get_json() or {}, partial=partial)
        for k, v in data.items():
            setattr(cab, k, v)
        db.session.commit()
        return ok({"id": cab.id})
    except IntegrityError as e:
        db.session.rollback()
        return fail(f"Integridad: {str(e.orig)}", 400)
    except SQLAlchemyError as e:
        db.session.rollback()
        return fail(str(e))


@bp_visitas.delete("/<int:idcab>")
def delete_visita(idcab):
    """Soft delete: ESTADO=0 para cabecera y sus detalles"""
    try:
        cab = cabRegITModel.query.get_or_404(idcab)
        cab.estado = 0
        detModel.query.filter_by(id_cab=idcab).update({"estado": 0})
        db.session.commit()
        return ok({"id": idcab})
    except SQLAlchemyError as e:
        db.session.rollback()
        return fail(str(e))

# ===== DETALLE =====

@bp_visitas.get("/<int:idcab>/detalles")
def list_detalles(idcab):
    cabRegITModel.query.get_or_404(idcab)  # valida existencia
    detalles = detModel.query.filter_by(id_cab=idcab, estado=1).all()
    return ok(detResponseDTO(many=True).dump(detalles))

@bp_visitas.post("/<int:idcab>/detalles")
def add_detalle(idcab):
    """Agregar 1 detalle a la cabecera"""
    try:
        cabRegITModel.query.get_or_404(idcab)
        payload = request.get_json() or {}
        payload["id_cab"] = idcab
        det = detCreateRequestDTO().load(payload)  # -> detModel
        db.session.add(det)
        db.session.commit()
        return ok({"id": det.id}, status=201)
    except IntegrityError as e:
        db.session.rollback()
        return fail(f"Integridad: {str(e.orig)}", 400)
    except SQLAlchemyError as e:
        db.session.rollback()
        return fail(str(e))

@bp_visitas.put("/<int:idcab>/detalles/<int:iddet>")
@bp_visitas.patch("/<int:idcab>/detalles/<int:iddet>")
def update_detalle(idcab, iddet):
    try:
        det = detModel.query.filter_by(id=iddet, id_cab=idcab).first_or_404()
        payload = request.get_json() or {}
        payload["id_cab"] = idcab
        partial = request.method == "PATCH"  # <-- PATCH parcial
        data = detUpdateRequestDTO().load(payload, partial=partial)
        for k, v in data.items():
            setattr(det, k, v)
        db.session.commit()
        return ok({"id": det.id})
    except IntegrityError as e:
        db.session.rollback()
        return fail(f"Integridad: {str(e.orig)}", 400)
    except SQLAlchemyError as e:
        db.session.rollback()
        return fail(str(e))


@bp_visitas.delete("/<int:idcab>/detalles/<int:iddet>")
def delete_detalle(idcab, iddet):
    """Soft delete del detalle"""
    try:
        det = detModel.query.filter_by(id=iddet, id_cab=idcab).first_or_404()
        det.estado = 0
        db.session.commit()
        return ok({"id": det.id})
    except SQLAlchemyError as e:
        db.session.rollback()
        return fail(str(e))

# ===== BULK / TRANSACCIÓN COMPLETA =====

@bp_visitas.post("/full")
def create_visita_full():
    """
    Crea la cabecera y un arreglo de detalles en UNA transacción.
    Body esperado:
    {
      "fecha_dig": "10/05/2025",
      "id_tec": "TEC001",
      "id_vend": "V12345",
      "id_clien": "CL0001",
      "id_motivo": 1,
      "correlativo": "000215",
      "detalles": [
        {"cod_prod": "PROD001"},
        {"cod_prod": "PROD002"}
      ]
    }
    """
    body = request.get_json() or {}
    detalles = body.pop("detalles", [])

    try:

        body["correlativo"] = next_correlativo_mssql(db.session, prefijo="FV")

        cab = cabRegITCreateRequestDTO().load(body)
        db.session.add(cab)
        db.session.flush()  # para obtener cab.id sin cerrar la transacción

        for d in detalles:
            d["id_cab"] = cab.id
            det = detCreateRequestDTO().load(d)
            db.session.add(det)

        db.session.commit()
        return ok({"id": cab.id, "detalles": len(detalles), "correlativo": cab.correlativo}, status=201)


    except (IntegrityError, SQLAlchemyError) as e:
        db.session.rollback()
        msg = f"Integridad: {str(e.orig)}" if isinstance(e, IntegrityError) else str(e)
        return fail(msg, 400 if isinstance(e, IntegrityError) else 500)

@bp_visitas.put("/<int:idcab>/detalles/bulk")
def replace_detalles(idcab):
    """
    Reemplaza (soft delete + inserción) todos los detalles de una cabecera.
    Body: { "detalles": [ {"cod_prod": "X"}, ... ] }
    """
    body = request.get_json() or {}
    items = body.get("detalles", [])
    try:
        cabRegITModel.query.get_or_404(idcab)
        # desactivar actuales
        detModel.query.filter_by(id_cab=idcab, estado=1).update({"estado": 0})
        db.session.flush()

        # insertar nuevos
        for d in items:
            d["id_cab"] = idcab
            det = detCreateRequestDTO().load(d)
            db.session.add(det)

        db.session.commit()
        return ok({"id_cab": idcab, "detalles": len(items)})
    except (IntegrityError, SQLAlchemyError) as e:
        db.session.rollback()
        msg = f"Integridad: {str(e.orig)}" if isinstance(e, IntegrityError) else str(e)
        return fail(msg, 400 if isinstance(e, IntegrityError) else 500)




@bp_visitas.put("/<int:idcab>/full")
def update_visita_full(idcab):
    """
    Actualiza cabecera y, opcionalmente, reemplaza todos los detalles.
    Reglas:
      - Omitir "detalles"  => no toca detalles
      - "detalles": []     => borra (soft delete) todos los detalles
      - "detalles": [...]  => reemplaza (soft delete + inserta nuevos)
    """
    body = request.get_json() or {}
    detalles = body.pop("detalles", None)  # None=no cambiar; []=borrar; list=reemplazar

    try:
        # 1) Cabecera
        cab = cabRegITModel.query.get_or_404(idcab)
        cambios = cabRegITUpdateRequestDTO().load(body, partial=True)  # permite parciales aquí
        for k, v in cambios.items():
            setattr(cab, k, v)

        # 2) Detalles (opcional)
        inserted = None
        if detalles is not None:
            if not isinstance(detalles, list):
                return fail("El campo 'detalles' debe ser un arreglo.", 400)

            # soft delete actuales
            detModel.query.filter_by(id_cab=idcab, estado=1).update({"estado": 0})
            db.session.flush()

            inserted = 0
            for d in detalles:
                d["id_cab"] = idcab
                det = detCreateRequestDTO().load(d)
                db.session.add(det)
                inserted += 1

        db.session.commit()
        return ok({
            "id": cab.id,
            "reemplazo_detalles": detalles is not None,
            "detalles_insertados": inserted
        })
    except ValidationError as e:
        db.session.rollback()
        return fail(e.messages, 400)
    except IntegrityError as e:
        db.session.rollback()
        return fail(f"Integridad: {str(e.orig)}", 400)
    except SQLAlchemyError as e:
        db.session.rollback()
        return fail(str(e))

# ==================LISTA PARA LA GRILLA (JOIN)==================


from flask import request
from sqlalchemy import and_, or_, func, literal_column
from sqlalchemy.orm import aliased

@bp_visitas.get("/grilla")
def grilla_visitas():
    # Parámetros
    page        = request.args.get("page", type=int, default=1)
    size        = request.args.get("size", type=int, default=20)
    qtext       = (request.args.get("q") or "").strip()
    id_tec      = request.args.get("id_tec")
    id_vend     = request.args.get("id_vend")
    id_clien    = request.args.get("id_clien")
    id_motivo   = request.args.get("id_motivo", type=int)
    fecha_desde = request.args.get("fecha_desde")  # 'dd/mm/yyyy'
    fecha_hasta = request.args.get("fecha_hasta")  # 'dd/mm/yyyy'
    usr_cod     = request.args.get("usr_cod")

    # Aliases/modelos
    Cab = cabRegITModel
    Cli = aliased(ClienteModel)        # SA1010
    Ven = aliased(VendedorModel)       # SA3010
    Mot = aliased(TipoVisitaModel)     # BKS0088
    Tec = aliased(TecnicosModel)       # BKS0087

    # Si fecha_dig es VARCHAR dd/mm/yyyy; si es DATE real, usa Cab.fecha_dig directo
    fconv = func.convert(literal_column("DATE"), Cab.fecha_dig, literal_column("103"))

    # Query base (LEFT JOIN + condiciones en el ON)
    query = (
        db.session.query(
            Cab.id.label("id"),
            Cab.correlativo.label("correlativo"),
            Tec.nombre.label("tecnico"),
            Ven.nombre.label("vendedor"),
            Cli.nombre.label("cliente"),
            Cab.fecha_dig.label("fecha_dig"),
            Mot.descripcion.label("motivo"),
        )
        .select_from(Cab)
        .outerjoin(
            Tec,
            and_(Tec.cod_tec == Cab.id_tec, Tec.estado == '1')
        )
        .outerjoin(
            Ven,
            and_(
                Ven.cod == Cab.id_vend,
                Ven.estado == '2',
                func.coalesce(Ven.delete, '') == ''
            )
        )
        .outerjoin(
            Cli,
            and_(
                Cli.cod == Cab.id_clien,
                Cli.estado == '2',
                func.coalesce(Cli.delete, '') == ''
            )
        )
        .outerjoin(Mot, Mot.id_visita == Cab.id_motivo)
        .filter(Cab.estado == 1)
        .filter(func.rtrim(func.ltrim(Cli.loja)) == '01')  # solo loja '01'
    )

    # Filtros dinámicos
    if id_tec:
        query = query.filter(Cab.id_tec == id_tec)
    if usr_cod:
        query = query.filter(Tec.userid == usr_cod)
    if id_vend:
        query = query.filter(Cab.id_vend == id_vend)
    if id_clien:
        query = query.filter(Cab.id_clien == id_clien)
    if id_motivo is not None:
        query = query.filter(Cab.id_motivo == id_motivo)

    if qtext:
        like = f"%{qtext}%"
        query = query.filter(
            or_(
                Cab.correlativo.like(like),
                func.coalesce(Ven.nombre, '').like(like),
                func.coalesce(Cli.nombre, '').like(like),
            )
        )

    # Fechas
    if fecha_desde:
        query = query.filter(
            fconv >= func.convert(literal_column("DATE"), fecha_desde, literal_column("103"))
        )
    if fecha_hasta:
        query = query.filter(
            fconv <= func.convert(literal_column("DATE"), fecha_hasta, literal_column("103"))
        )

    # 🔧 Elimina duplicados del JOIN agrupando por todas las columnas seleccionadas
    query = query.group_by(
        Cab.id,
        Cab.correlativo,
        Tec.nombre,
        Ven.nombre,
        Cli.nombre,
        Cab.fecha_dig,
        Mot.descripcion,
    )

    # Orden
    query = query.order_by(fconv.desc(), Cab.correlativo.desc())

    # Paginación
    pag = query.paginate(page=page, per_page=size, error_out=False)

    # Serialización
    items = [
        {
            "id": r.id,
            "correlativo": r.correlativo,
            "tecnico": r.tecnico,
            "vendedor": r.vendedor,
            "cliente": r.cliente,
            "fecha_dig": r.fecha_dig,
            "motivo": r.motivo,
        }
        for r in pag.items
    ]

    return ok({
        "items": items,
        "page": pag.page,
        "pages": pag.pages,
        "total": pag.total,
    })