# app/routes/maestros/Adjunto.py

import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.extensions import db
from app.services.graph_files import (
    upload_small,
    create_anonymous_link,
    upload_large_stream,
    get_thumbnail_url,
)
from app.models.transacciones import AdjuntoModel
from app.services.reclamo_notificaciones import notify_reclamo_creado
from app.models.transacciones.md_SolicitudReclamo import SolicitudReclamoModel
from app.routes.maestros.SolicitudReclamo import enviar_correo_reclamo 

adjuntos_bp = Blueprint("adjuntos", __name__, url_prefix="/api/adjuntos")


@adjuntos_bp.get("/reclamo/<int:id_reclamo>")
def listar_adjuntos_por_reclamo(id_reclamo: int):
    q = (
        AdjuntoModel.query
        .filter_by(id_reclamo=id_reclamo)
        .order_by(AdjuntoModel.orden.asc(), AdjuntoModel.id_adjunto.asc())
        .all()
    )

    data = [{
        "id_adjunto": r.id_adjunto,
        "id_reclamo": r.id_reclamo,
        "file_name": r.file_name,
        "ruta_imagen": r.ruta_imagen,
        "drive_item_id": r.drive_item_id,
        "thumbnail_url": r.thumbnail_url,
        "content_type": r.content_type,
        "size_bytes": r.size_bytes,
        "orden": r.orden,
        "creado_en": r.creado_en.isoformat() if r.creado_en else None,
    } for r in q]

    return jsonify(data), 200


FOUR_MB = 4 * 1024 * 1024


def _size_of_filestorage(fs) -> int | None:
    """
    Intenta determinar el tamaño del FileStorage SIN consumir el stream.
    Devuelve None si no es posible.
    """
    size_hint = getattr(fs, "content_length", None)

    try:
        pos = fs.stream.tell()
        fs.stream.seek(0, os.SEEK_END)
        size_seek = fs.stream.tell()
        fs.stream.seek(pos)
    except Exception:
        size_seek = None

    return size_hint or size_seek


@adjuntos_bp.post("/reclamo/<int:id_reclamo>/upload")
def subir_adjunto(id_reclamo: int):
    """
    Sube UN solo adjunto a SharePoint y lo registra en BKS0092_ADJUNTOS.
    ESTE ENDPOINT YA NO ENVÍA CORREO para evitar notificaciones duplicadas.
    """
    try:
        # 1) validar archivo
        if "file" not in request.files:
            return jsonify({"ok": False, "message": "Falta el campo 'file' (multipart/form-data)."}), 400

        f = request.files["file"]
        if not f or not f.filename:
            return jsonify({"ok": False, "message": "Archivo sin nombre."}), 400

        filename = secure_filename(f.filename)
        size = _size_of_filestorage(f)

        # 2) subir (auto small/large)
        if size is not None and size > FOUR_MB:
            up = upload_large_stream(f.stream, filename)   # > 4 MB
        else:
            file_bytes = f.read()
            if not file_bytes:
                return jsonify({"ok": False, "message": "Archivo vacío."}), 400
            up = upload_small(file_bytes, filename)        # ≤ 4 MB

        item_id = up["id"]
        file_name = up["name"]
        size_bytes = up.get("size")
        content_type = (up.get("file") or {}).get("mimeType")

        # 3) crear link público + miniatura
        thumbnail_url = get_thumbnail_url(item_id)  # "small" | "medium" | "large"
        public_url = create_anonymous_link(item_id)

        # 4) calcular siguiente orden y guardar en BD
        ultimo = (
            AdjuntoModel.query
            .filter_by(id_reclamo=id_reclamo)
            .order_by(AdjuntoModel.orden.desc())
            .first()
        )
        next_orden = (ultimo.orden + 1) if ultimo else 1

        adj = AdjuntoModel(
            id_reclamo=id_reclamo,
            file_name=file_name,
            ruta_imagen=public_url,
            drive_item_id=item_id,
            content_type=content_type,
            size_bytes=size_bytes,
            orden=next_orden,
            thumbnail_url=thumbnail_url,
        )
        db.session.add(adj)
        db.session.commit()

        # IMPORTANTE: aquí YA NO se llama notify_reclamo_creado()
        # Para enviar el correo con todos los adjuntos, usar /upload-multiple
        # o un endpoint separado de notificación.

        return jsonify({
            "ok": True,
            "id_adjunto": adj.id_adjunto,
            "id_reclamo": id_reclamo,
            "file_name": file_name,
            "ruta_imagen": public_url,
            "drive_item_id": item_id,
            "content_type": content_type,
            "size_bytes": size_bytes,
            "orden": adj.orden,
            "thumbnail_url": thumbnail_url,
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"ok": False, "error": type(e).__name__, "message": str(e)}), 500


@adjuntos_bp.post("/reclamo/<int:id_reclamo>/upload-multiple")
def subir_adjuntos_multiples(id_reclamo: int):
    """
    Sube VARIOS adjuntos en una sola petición.
    Al finalizar, envía UN SOLO correo con todos los enlaces del reclamo.
    - es_nuevo = True  -> primera vez que el reclamo tiene adjuntos  -> banner "Nuevo reclamo..."
    - es_nuevo = False -> reclamo ya tenía adjuntos (actualización)   -> banner "Formulario fue modificado..."
    """
    try:
        # 1) Obtener lista de archivos: key recomendada 'files'
        files = request.files.getlist("files")

        # Si no mandan exactamente 'files', recolectamos todo lo que venga
        if not files:
            collected = []
            for k in request.files.keys():
                collected.extend(request.files.getlist(k))
            files = collected

        if not files:
            return jsonify({
                "ok": False,
                "message": "Falta el campo 'files' (multipart/form-data múltiple). "
                           "Usa la misma key 'files' para cada archivo."
            }), 400

        resultados_ok = []
        resultados_error = []

        # 🔹 Antes de grabar nuevos adjuntos, vemos si el reclamo ya tenía alguno
        adjuntos_previos = (
            AdjuntoModel.query
            .filter_by(id_reclamo=id_reclamo)
            .count()
        )
        es_nuevo = (adjuntos_previos == 0)

        # 2) Procesar cada archivo
        for f in files:
            try:
                if not f or not f.filename:
                    raise ValueError("Archivo sin nombre.")

                filename = secure_filename(f.filename)
                size = _size_of_filestorage(f)

                # 2.1) Subir (small/large)
                if size is not None and size > FOUR_MB:
                    up = upload_large_stream(f.stream, filename)
                else:
                    file_bytes = f.read()
                    if not file_bytes:
                        raise ValueError("Archivo vacío.")
                    up = upload_small(file_bytes, filename)

                item_id = up["id"]
                file_name = up["name"]
                size_bytes = up.get("size")
                content_type = (up.get("file") or {}).get("mimeType")
                public_url = create_anonymous_link(item_id)
                thumbnail_url = get_thumbnail_url(item_id)

                # 3) Calcular siguiente orden y guardar en BD
                ultimo = (
                    AdjuntoModel.query
                    .filter_by(id_reclamo=id_reclamo)
                    .order_by(AdjuntoModel.orden.desc())
                    .first()
                )
                next_orden = (ultimo.orden + 1) if ultimo else 1

                adj = AdjuntoModel(
                    id_reclamo=id_reclamo,
                    file_name=file_name,
                    ruta_imagen=public_url,
                    drive_item_id=item_id,
                    content_type=content_type,
                    size_bytes=size_bytes,
                    orden=next_orden,
                    thumbnail_url=thumbnail_url,
                )
                db.session.add(adj)
                db.session.commit()

                resultados_ok.append({
                    "id_adjunto": adj.id_adjunto,
                    "file_name": file_name,
                    "ruta_imagen": public_url,
                    "drive_item_id": item_id,
                    "content_type": content_type,
                    "size_bytes": size_bytes,
                    "orden": adj.orden,
                    "thumbnail_url": thumbnail_url,
                })

            except Exception as e:
                db.session.rollback()
                resultados_error.append({
                    "file": getattr(f, "filename", None),
                    "error": str(e)
                })

        # 4) Si por lo menos UN archivo subió bien, enviamos el correo UNA sola vez
        if resultados_ok:
            try:
                rec = SolicitudReclamoModel.query.get(id_reclamo)
                if not rec:
                    current_app.logger.warning(
                        f"[subir_adjuntos_multiples] Reclamo {id_reclamo} no encontrado al enviar correo."
                    )
                else:
                    current_app.logger.info(
                        f"[subir_adjuntos_multiples] enviando correo para reclamo "
                        f"{id_reclamo}, es_nuevo={es_nuevo}"
                    )
                    enviar_correo_reclamo(rec, es_nuevo=es_nuevo)
            except Exception as e:
                # Importante: si falla el correo NO reventamos la respuesta al front
                current_app.logger.error(
                    f"[subir_adjuntos_multiples] Error enviando correo de reclamo "
                    f"{id_reclamo}: {e}"
                )

        # 5) Status HTTP según hubo éxito o no
        status = (
            201 if resultados_ok and not resultados_error
            else 207 if resultados_ok
            else 400
        )

        return jsonify({
            "ok": bool(resultados_ok),
            "subidos": resultados_ok,
            "errores": resultados_error
        }), status

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(
            f"[subir_adjuntos_multiples] EXCEPCIÓN GENERAL: {e}"
        )
        return jsonify({"ok": False, "message": str(e)}), 500
