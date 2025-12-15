#-->  routes/maestros/SolicitudReclamo.py
from flask import Blueprint, request, jsonify, render_template, current_app
from app.services.seguridad import es_usuario_calidad_por_id, obtener_grupos_usuario,obtener_usr_cod_por_recno

from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError
from sqlalchemy import func, text
from datetime import datetime
from app.extensions import db
from app.services.graph_mail import send_mail_graph, build_reclamo_email_body

# Rutas de modelos/DTOs según tu estructura
from app.models.transacciones.md_Adjunto import AdjuntoModel
from app.models.maestros.md_usuarios import Usuario

from datetime import datetime

from app.models.transacciones.md_SolicitudReclamo import SolicitudReclamoModel
from app.models.transacciones.md_ReclamoMensaje import ReclamoMensajeModel
from app.schemas.maestros.SolicitudReclamoDTO import (
    SolicitudReclamoResponseDTO,
    ReclamoCreateRequestDTO,
    ReclamoUpdateRequestDTO,

    
)
from app.schemas.maestros.ReclamoEstadoCalidadRequestDTO import (
    ReclamoEstadoCalidadRequestDTO,
)

from app.schemas.maestros.ReclamoMensajeDTO import (
    ReclamoMensajeCreateRequestDTO,
    ReclamoMensajeResponseDTO,
)


solicitud_reclamo_bp = Blueprint(
    "solicitud_reclamo_bp",
    __name__,
    url_prefix="/api/reclamos"
)

# Schemas reutilizables
resp_schema = SolicitudReclamoResponseDTO()
resp_list_schema = SolicitudReclamoResponseDTO(many=True)
create_schema = ReclamoCreateRequestDTO()
update_schema = ReclamoUpdateRequestDTO()
reclamo_estado_calidad_schema = ReclamoEstadoCalidadRequestDTO()
reclamo_schema = SolicitudReclamoResponseDTO()
reclamo_mensaje_create_schema = ReclamoMensajeCreateRequestDTO()
reclamo_mensaje_response_schema = ReclamoMensajeResponseDTO()
resp_list_schema = SolicitudReclamoResponseDTO(many=True)


def _next_documento(prefix: str = "REC-", width: int = 6) -> str:
    """
    Genera el siguiente correlativo tipo REC-000123.
    Usa la columna física NUM_DOC de la tabla BKS0092.
    """
    table = SolicitudReclamoModel.__tablename__  # debería ser BKS0092
    doc_column = "NUM_DOC"  # nombre REAL de la columna en SQL Server

    sql = text(f"""
        SELECT MAX(CAST(REPLACE({doc_column}, :prefix, '') AS INT))
        FROM {table}
        WHERE {doc_column} LIKE :likeprefix
    """)

    maxn = db.session.execute(sql, {
        "prefix": prefix,
        "likeprefix": f"{prefix}%"
    }).scalar()

    nxt = (maxn or 0) + 1
    return f"{prefix}{nxt:0{width}d}"


# ===================== Helper para correo =====================
def enviar_correo_reclamo(rec: SolicitudReclamoModel, es_nuevo: bool = True) -> None:
    """
    Arma el HTML con build_reclamo_email_body y envía el correo por Graph.
    """

    # 1) Título y asunto según sea nuevo o editado
    if es_nuevo:
        titulo_banner = "Nuevo reclamo registrado"
        asunto = f"Nuevo reclamo N° {rec.documento} - {rec.cliente}"
    else:
        titulo_banner = "Formulario fue modificado"
        asunto = f"Reclamo actualizado N° {rec.documento} - {rec.cliente}"

    # 2) Diccionario con los datos del reclamo que usa el template
    reclamo_data = {
        "num_doc": rec.documento,
        "documento": rec.documento,
        "fecha_emision": rec.fecha_emision,
        "cliente": rec.cliente,
        "telefono_cliente": rec.telefono_cliente,
        "correo_cliente": rec.correo_cliente,
        "direccion_cliente": rec.direccion_cliente,
        "cod_prod": rec.cod_prod,
        "nombre_prod": rec.nombre_prod,
        "lote_prod": rec.lote_prod,
        "cantidad_reclamada": rec.cantidad_reclamada,
        "fecha_despacho": rec.fecha_despacho,
        "tipo_reclamo": rec.tipo_reclamo,
        "nombre_vendedor": rec.nombre_vendedor,
        "descripcion_reclamo": rec.descripcion_reclamo,
    }

    # 3) Leer adjuntos desde la tabla de adjuntos
    try:
        # ⚠️ AJUSTA: si tu campo no se llama id_reclamo o no tienes estado
        adjuntos = AdjuntoModel.query.filter_by(
            id_reclamo=rec.id
            # , estado=1  # descomenta si manejas soft-delete
        ).all()
    except Exception as e:
        current_app.logger.error(
            f"[enviar_correo_reclamo] Error consultando adjuntos: {e}"
        )
        adjuntos = []

    # 4) Construir lista de URLs de adjuntos (para el bloque "Adjuntos")
    # ⚠️ AJUSTA: si tu campo no se llama ruta_imagen / url_archivo
    adjuntos_urls = []
    for a in adjuntos:
        url = getattr(a, "ruta_imagen", None) or getattr(a, "url_archivo", None)
        if url:
            adjuntos_urls.append(url)

    # 5) Construir el HTML del correo
    try:
        html_body = build_reclamo_email_body(
            reclamo_data,
            adjuntos_urls,
            titulo_banner,
        )
    except Exception as e:
        current_app.logger.error(
            f"[enviar_correo_reclamo] Error armando HTML del correo: {e}"
        )
        return

    # 6) Destinatarios
    destinatarios = [
        "zoila.saavedra@bakels.com.pe",
        "calidad@bakels.com.pe",
        "alberto.vasquez@bakels.com.pe",
    ]

    if not destinatarios:
        current_app.logger.warning(
            "[enviar_correo_reclamo] No hay destinatarios configurados."
        )
        return

    # 7) Enviar correo por Graph
    try:
        send_mail_graph(
            from_address="notificaciones@bakels.com.pe",
            to_addresses=destinatarios,
            subject=asunto,
            html_body=html_body,
        )
    except Exception as e:
        current_app.logger.error(
            f"[enviar_correo_reclamo] Error enviando correo: {e}"
        )
# ===================== Crear =====================
@solicitud_reclamo_bp.post("")
def crear_reclamo():
    try:
        payload = create_schema.load(request.get_json(silent=True) or {})

        # si no viene documento, generamos correlativo
        if not payload.get("documento"):
            payload["documento"] = _next_documento(prefix="REC-", width=6)

        # 👇 aquí esperamos que el front NOS ENVÍE id_usuario_registro
        if not payload.get("id_usuario_registro"):
            return jsonify({
                "message": "Falta el campo id_usuario_registro en el payload"
            }), 400

        nuevo = SolicitudReclamoModel(**payload)  # estado = 1 por defecto en el modelo
        db.session.add(nuevo)
        db.session.commit()

       
        # Ya NO enviamos correo aquí.
        # El correo (nuevo reclamo) se enviará al finalizar
        # el endpoint de upload-multiple, cuando los adjuntos
        # ya estén grabados en BD.

        return jsonify(resp_schema.dump(nuevo)), 201

    except ValidationError as ve:
        return jsonify({"message": "Datos inválidos", "errors": ve.messages}), 400

    except IntegrityError as ie:
        db.session.rollback()
        return jsonify({"message": "Error de integridad", "detail": str(ie.orig)}), 409

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al crear reclamo", "detail": str(e)}), 500


# -------------------- Actualizar (PUT) --------------------
@solicitud_reclamo_bp.put("/<int:id>")
def actualizar_reclamo(id: int):
    try:
        # Leer body crudo
        raw_data = request.get_json(silent=True) or {}

        # 🧍‍♂️ id del usuario que intenta actualizar (recno: 101, 112, etc.)
        id_usuario_actual_recno = raw_data.get("id_usuario_actual")
        if not id_usuario_actual_recno:
            return jsonify({"message": "id_usuario_actual es requerido"}), 400

        # Evitar que id_usuario_actual entre al schema de actualización
        payload = dict(raw_data)
        payload.pop("id_usuario_actual", None)

        # Validar cambios con tu schema
        cambios = update_schema.load(payload)

        reclamo = SolicitudReclamoModel.query.get(id)

        if not reclamo or reclamo.estado == 0:
            return jsonify({"message": "Reclamo no encontrado"}), 404

        # 🧭 Mapear recno -> USR_ID real de Protheus
        usr_cod_actual = obtener_usr_cod_por_recno(id_usuario_actual_recno)

        es_calidad = False
        if usr_cod_actual:
            es_calidad = es_usuario_calidad_por_id(usr_cod_actual)

        # DEBUG
        print(
            f"[actualizar_reclamo] id={id}, estado={reclamo.estado}, "
            f"id_usuario_actual_recno={id_usuario_actual_recno}, "
            f"usr_cod_actual={usr_cod_actual}, es_calidad={es_calidad}"
        )

        # 🚫 Si el reclamo está CERRADO (2) y NO es usuario de calidad -> bloquear
        if reclamo.estado == 2 and not es_calidad:
            return jsonify({
                "message": "El reclamo está cerrado y no puede ser modificado por este usuario."
            }), 403

        # ✅ Aplicar cambios
        for k, v in cambios.items():
            setattr(reclamo, k, v)

        reclamo.fecha_mod = datetime.now()
        db.session.commit()

        # 👇 leer flag skip_email de la querystring
        skip_email = request.args.get("skip_email", "0") == "1"
        current_app.logger.info(
            f"[actualizar_reclamo] id={id}, skip_email={skip_email}, args={dict(request.args)}"
        )

        if not skip_email:
            try:
                enviar_correo_reclamo(reclamo, es_nuevo=False)
            except Exception as e:
                current_app.logger.error(
                    f"[actualizar_reclamo] ERROR enviando correo: {e}"
                )

        return jsonify(resp_schema.dump(reclamo)), 200

    except ValidationError as ve:
        return jsonify({"message": "Datos inválidos", "errors": ve.messages}), 400

    except IntegrityError as ie:
        db.session.rollback()
        return jsonify({"message": "Error de integridad", "detail": str(ie.orig)}), 409

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al actualizar reclamo", "detail": str(e)}), 500





# -------------------- “Eliminar” (Soft Delete -> estado = 0) --------------------
@solicitud_reclamo_bp.delete("/<int:id>")
def eliminar_reclamo(id: int):
    try:
        reclamo = SolicitudReclamoModel.query.get(id)
        if not reclamo or reclamo.estado == 0:
            return jsonify({"message": "Reclamo no encontrado"}), 404

        reclamo.estado = 0
        reclamo.fecha_mod = func.current_timestamp()
        db.session.commit()
        return jsonify({"message": "Reclamo deshabilitado (estado=0)"}), 200
    except IntegrityError as ie:
        db.session.rollback()
        return jsonify({"message": "Error de integridad", "detail": str(ie.orig)}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error al deshabilitar reclamo", "detail": str(e)}), 500


# -------------------- Listar activos --------------------
@solicitud_reclamo_bp.get("")
def listar_reclamos():
    # leer querystring ?id_usuario_registro=101  (R_E_C_N_O_)
    id_usuario_recno = request.args.get("id_usuario_registro")  # string

    if not id_usuario_recno:
        return jsonify({"message": "id_usuario_registro es requerido"}), 400

    # 1) Mapeamos: recno (101) -> USR_ID real ('000105')
    usr_cod = obtener_usr_cod_por_recno(id_usuario_recno)

    if not usr_cod:
        # Si no encontramos el usuario en SYS_USR, lo tratamos como no-calidad
        print(f"No se encontró usr_cod para recno {id_usuario_recno}")
        es_calidad = False
        grupos = []
    else:
        # 2) Obtenemos grupos usando el USR_ID real
        grupos = obtener_grupos_usuario(usr_cod)
        print(f"Grupos del usuario {usr_cod} (recno {id_usuario_recno}): {grupos}")

        # 3) Vemos si pertenece al grupo 000006
        es_calidad = es_usuario_calidad_por_id(usr_cod)

    # Base: todos los reclamos
    qs = SolicitudReclamoModel.query

    # Si NO es calidad -> solo ve sus propios reclamos (por recno)
    if not es_calidad:
        qs = qs.filter(SolicitudReclamoModel.id_usuario_registro == id_usuario_recno)

    # Calidad ve todos, así que no filtramos por id_usuario_registro
    qs = qs.order_by(SolicitudReclamoModel.id.desc())

    reclamos = qs.all()
    data = resp_list_schema.dump(reclamos)

    # 👇 Inyectamos estado e id_usuario_registro en cada item de la lista
    for item, rec in zip(data, reclamos):
        item["estado"] = rec.estado
        item["id_usuario_registro"] = rec.id_usuario_registro

    return jsonify(data), 200







# --------------------- Obtener por num_doc (documento) --------------------
@solicitud_reclamo_bp.get("/<string:num_doc>")
def obtener_reclamo(num_doc: str):
    # Buscar por campo NUM_DOC (documento) y que esté activo
    r = SolicitudReclamoModel.query.filter_by(documento=num_doc, estado=1).first()

    if not r:
        return jsonify({"message": f"Reclamo con documento {num_doc} no encontrado"}), 404

    return jsonify(resp_schema.dump(r)), 200


# ========== NUEVO: OBTENER RECLAMO POR ID (si lo necesitas) ==========
# OJO: con el url_prefix="/api/reclamos", esta ruta expone:
#   GET /api/reclamos/id/<id_reclamo>
@solicitud_reclamo_bp.get("/id/<int:id_reclamo>")
def obtener_reclamo_por_id(id_reclamo: int):
    rec = SolicitudReclamoModel.query.get(id_reclamo)
    if not rec:
        return jsonify({"message": "Reclamo no encontrado"}), 404

    data = resp_schema.dump(rec)

    # 👇 agregamos explícitamente estos campos
    data["estado"] = rec.estado
    data["id_usuario_registro"] = rec.id_usuario_registro

    return jsonify(data), 200


@solicitud_reclamo_bp.route('/<int:id>/estado-calidad-admin', methods=['PUT'])
def actualizar_estado_calidad_admin(id):
    data = request.get_json() or {}

    errors = reclamo_estado_calidad_schema.validate(data)
    if errors:
        return jsonify({"message": "Error de validación", "errors": errors}), 400

    nuevo_estado = data.get("estado")
    respuesta_calidad = data.get("respuesta_calidad")
    id_usuario_calidad_recno = data.get("id_usuario_calidad")  # recno, ej. 101

    if not id_usuario_calidad_recno:
        return jsonify({"message": "id_usuario_calidad es requerido"}), 400

    # 1) Mapear recno (101) -> USR_ID real Protheus ('000105')
    usr_cod_calidad = obtener_usr_cod_por_recno(id_usuario_calidad_recno)
    if not usr_cod_calidad:
        return jsonify({
            "message": "Usuario de calidad no encontrado en SYS_USR"
        }), 400

    # 2) Validar que pertenezca al grupo de CALIDAD (000006)
    if not es_usuario_calidad_por_id(usr_cod_calidad):
        return jsonify({
            "message": "No autorizado: el usuario no pertenece al grupo de Calidad (000006)"
        }), 403

    # 3) Buscar reclamo
    reclamo = SolicitudReclamoModel.query.get(id)
    if not reclamo:
        return jsonify({"message": "Reclamo no encontrado"}), 404

    # 4) Aseguramos que estado sea int
      # 4) Aseguramos que estado sea int
    try:
        nuevo_estado_int = int(nuevo_estado)
    except (TypeError, ValueError):
        return jsonify({"message": "El estado debe ser numérico"}), 400

    reclamo.estado = nuevo_estado_int

    # 🟢 DEBUG: ver qué valores tenemos
    print("DEBUG estado recibido:", nuevo_estado, "->", nuevo_estado_int)

    # 5) Fecha de cierre
    if nuevo_estado_int == 2:  # 2 = CERRADO
        reclamo.fecha_cierre = datetime.now().strftime("%Y-%m-%d")
    else:
        reclamo.fecha_cierre = None

    print("DEBUG antes de commit. estado:", reclamo.estado, "fecha_cierre:", reclamo.fecha_cierre)


    reclamo.respuesta_calidad = respuesta_calidad
    reclamo.id_usuario_calidad = id_usuario_calidad_recno  # guardamos recno (101)
    reclamo.FECHA_UPDATE = datetime.now().strftime("%Y-%m-%d")

    db.session.commit()

    return jsonify(reclamo_schema.dump(reclamo)), 200




# ===================== Rutas para mensajes del reclamo-CHAT CON USUARIOS =====================
@solicitud_reclamo_bp.route('/<int:id_reclamo>/mensajes', methods=['GET'])
def listar_mensajes_reclamo(id_reclamo):
    # Verificar que exista
    reclamo = SolicitudReclamoModel.query.get(id_reclamo)
    if not reclamo:
        return jsonify({"message": "Reclamo no encontrado"}), 404

    # Traer mensajes, ordenados
    mensajes = (
        db.session.query(ReclamoMensajeModel, Usuario.usr_nom)
        .join(Usuario, Usuario.usr_id == ReclamoMensajeModel.id_usuario, isouter=True)
        .filter(ReclamoMensajeModel.id_reclamo == id_reclamo)
        .order_by(ReclamoMensajeModel.fecha_envio.asc())
        .all()
    )

    result = []
    for msg, nombre in mensajes:
        payload = reclamo_mensaje_response_schema.dump(msg)
        payload["nombre_usuario"] = nombre  # ← agregamos el nombre aquí
        result.append(payload)

    return jsonify(result), 200

# -------------------- Crear mensaje para un reclamo  CHAT --------------------
@solicitud_reclamo_bp.route('/<int:id_reclamo>/mensajes', methods=['POST'])
def crear_mensaje_reclamo(id_reclamo):
    data = request.get_json() or {}

    errors = reclamo_mensaje_create_schema.validate(data)
    if errors:
        return jsonify({"message": "Error de validación", "errors": errors}), 400

    # Verificar que el reclamo exista
    reclamo = SolicitudReclamoModel.query.get(id_reclamo)
    if not reclamo:
        return jsonify({"message": "Reclamo no encontrado"}), 404

    id_usuario_recno = data.get("id_usuario")          # recno del usuario que envía
    mensaje_texto = (data.get("mensaje") or "").strip()

    if not id_usuario_recno:
        return jsonify({"message": "id_usuario es requerido"}), 400

    if not mensaje_texto:
        return jsonify({"message": "El mensaje no puede estar vacío"}), 400

    # 1) Mapear recno (101) -> USR_ID real Protheus ('000105')
    usr_cod = obtener_usr_cod_por_recno(id_usuario_recno)

    es_calidad = False
    if usr_cod:
        es_calidad = es_usuario_calidad_por_id(usr_cod)

    # 2) Si el reclamo está CERRADO (2) y NO es usuario de calidad -> bloquear
    if reclamo.estado == 2 and not es_calidad:
        return jsonify({
            "message": "El reclamo está cerrado y este usuario no puede enviar más mensajes."
        }), 403

    # 3) Crear el mensaje (permitido: reclamo abierto o usuario de calidad)
    nuevo_mensaje = ReclamoMensajeModel(
        id_reclamo=id_reclamo,
        id_usuario=id_usuario_recno,   # recno del usuario que envía
        mensaje=mensaje_texto,
    )

    db.session.add(nuevo_mensaje)
    db.session.commit()

    # ==========================
    #  ENVÍO DE CORREO AQUÍ
    # ==========================
    try:
        frontend_url = current_app.config.get("FRONTEND_BASE_URL", "http://localhost:5173")
        link_conversacion = f"{frontend_url}/calidad/reclamos/{id_reclamo}"

        # Ojo: en tu modelo Usuario, usr_id es el R_E_C_N_O_ (recno)
        try:
            id_usuario_int = int(id_usuario_recno)
        except (TypeError, ValueError):
            id_usuario_int = None

        usuario = None
        if id_usuario_int is not None:
            usuario = Usuario.query.filter_by(usr_id=id_usuario_int).first()

        # Nombre limpio
        if usuario and usuario.usr_nom:
            nombre_usuario = usuario.usr_nom.strip()
        else:
            nombre_usuario = f"Usuario {id_usuario_recno}"

        # Mensaje limpio (con saltos de línea para HTML)
        mensaje_limpio = mensaje_texto.replace("\n", "<br/>")

        documento = getattr(reclamo, "documento", None) or f"ID {reclamo.ID_RECLAMO}"
        asunto = f"{nombre_usuario} envió un mensaje {documento}"

        cuerpo_html = f"""
            <table width="100%" cellpadding="0" cellspacing="0" style="font-family: Arial, sans-serif; background-color:#f3f4f6; padding:20px 0;">
            <tr>
                <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:12px; overflow:hidden; box-shadow:0 2px 6px rgba(15,23,42,0.15);">
                    <!-- HEADER AZUL -->
                    <tr>
                    <td style="background-color:#252850; padding:12px 20px; color:#ffffff;">
                        <table width="100%" cellpadding="0" cellspacing="0">
                        <tr>
                            <td style="font-size:14px; font-weight:bold; display:flex; align-items:center;">
                            <span style="display:inline-flex; align-items:center; justify-content:center; width:24px; height:24px; border-radius:999px; background-color:rgba(255,255,255,0.18); margin-right:8px;">
                                &#128172;
                            </span>
                            <span>Nuevo mensaje en el reclamo <span style="font-weight:700;">{documento}</span></span>
                            </td>
                        </tr>
                        <tr>
                            <td style="font-size:12px; opacity:0.85; padding-top:2px;">
                            Conversación registrada en el módulo de Calidad.
                            </td>
                        </tr>
                        </table>
                    </td>
                    </tr>

                    <!-- CONTENIDO -->
                    <tr>
                    <td style="padding:16px 20px 4px 20px; font-size:13px; color:#111827;">
                        <p style="margin:0 0 8px 0;">
                        Se ha registrado un nuevo mensaje en el reclamo <strong>{documento}</strong>.
                        </p>
                        <p style="margin:0 0 8px 0;">
                        <strong>Remitente:</strong> {nombre_usuario}
                        </p>
                        <p style="margin:0 0 4px 0;"><strong>Mensaje:</strong></p>
                    </td>
                    </tr>

                    <!-- MENSAJE -->
                    <tr>
                    <td style="padding:0 20px 8px 20px;">
                        <div style="border-left:4px solid #252850; background-color:#f9fafb; padding:10px 12px; font-size:13px; color:#111827;">
                        {mensaje_limpio}
                        </div>
                    </td>
                    </tr>

                    <!-- BOTÓN IR A LA CONVERSACIÓN -->
                    <tr>
                    <td align="center" style="padding:14px 20px 18px 20px;">
                        <a href="{link_conversacion}"
                        style="display:inline-block; background-color:#252850; color:#ffffff; text-decoration:none; 
                                padding:8px 18px; border-radius:999px; font-size:13px; font-weight:600;">
                        Ir a la conversación
                        </a>
                    </td>
                    </tr>

                    <!-- FOOTER -->
                    <tr>
                    <td style="border-top:1px solid #e5e7eb; padding:10px 20px; font-size:11px; color:#6b7280;">
                        Este es un mensaje automático de MAKUTO-SYS - Módulo de Reclamos. Responda en el formulario de calidad.
                    </td>
                    </tr>
                </table>
                </td>
            </tr>
            </table>
            """
        destinatarios = [
            "zoila.saavedra@bakels.com.pe",
            "calidad@bakels.com.pe",
            "alberto.vasquez@bakels.com.pe",
        ]

        send_mail_graph(
            from_address="notificaciones@bakels.com.pe",
            to_addresses=destinatarios,
            subject=asunto,
            html_body=cuerpo_html,
        )

    except Exception as e:
        current_app.logger.error(f"[Chat Reclamo] Error al enviar correo: {e}")

    # Construir la respuesta al front
    result = reclamo_mensaje_response_schema.dump(nuevo_mensaje)
    result["nombre_usuario"] = (
        usuario.usr_nom.strip()
        if 'usuario' in locals() and usuario and usuario.usr_nom
        else None
    )

    return jsonify(result), 201
