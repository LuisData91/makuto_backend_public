# app/routes/maestros/Adjunto.py
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
from app.db import db
from app.services.graph_files import upload_small, create_anonymous_link,upload_large_stream
from app.models.transacciones import AdjuntoModel
from app.schemas.maestros.AdjuntoDTO import adjuntos_schema  
from app.services.graph_files import get_thumbnail_url


adjuntos_bp = Blueprint("adjuntos", __name__, url_prefix="/api/adjuntos")

@adjuntos_bp.get("/reclamo/<int:id_reclamo>")
def listar_adjuntos_por_reclamo(id_reclamo: int):
    q = (AdjuntoModel.query
         .filter_by(id_reclamo=id_reclamo)
         .order_by(AdjuntoModel.orden.asc(), AdjuntoModel.id_adjunto.asc())
         .all())

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
    # Algunos servidores adjuntan content_length
    size_hint = getattr(fs, "content_length", None)

    try:
        # Si el stream es seekable, medimos sin consumir
        pos = fs.stream.tell()
        fs.stream.seek(0, os.SEEK_END)
        size_seek = fs.stream.tell()
        fs.stream.seek(pos)
    except Exception:
        size_seek = None

    return size_hint or size_seek


@adjuntos_bp.post("/reclamo/<int:id_reclamo>/upload")
def subir_adjunto(id_reclamo: int):
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

        item_id      = up["id"]
        file_name    = up["name"]
        size_bytes   = up.get("size")
        content_type = (up.get("file") or {}).get("mimeType")

        # 3) crear link público
        thumbnail_url = get_thumbnail_url(item_id)  # "small" | "medium" | "large"

        public_url = create_anonymous_link(item_id)

        # 4) calcular siguiente orden y guardar en BD
        ultimo = (AdjuntoModel.query
                  .filter_by(id_reclamo=id_reclamo)
                  .order_by(AdjuntoModel.orden.desc())
                  .first())
        next_orden = (ultimo.orden + 1) if ultimo else 1

        adj = AdjuntoModel(
            id_reclamo    = id_reclamo,
            file_name     = file_name,
            ruta_imagen   = public_url,
            drive_item_id = item_id,
            content_type  = content_type,
            size_bytes    = size_bytes,
            orden         = next_orden,
            thumbnail_url = thumbnail_url,
        )
        db.session.add(adj)
        db.session.commit()

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
    try:
        # 1) obtener lista de archivos (key recomendada: 'files')
        files = request.files.getlist("files")

        # tolerante: si no pasaron 'files', recolecta todo lo que venga
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

        for f in files:
            try:
                if not f or not f.filename:
                    raise ValueError("Archivo sin nombre.")

                filename = secure_filename(f.filename)
                size = _size_of_filestorage(f)

                # 2) subir (auto small/large)
                if size is not None and size > FOUR_MB:
                    up = upload_large_stream(f.stream, filename)
                else:
                    file_bytes = f.read()
                    if not file_bytes:
                        raise ValueError("Archivo vacío.")
                    up = upload_small(file_bytes, filename)

                item_id      = up["id"]
                file_name    = up["name"]
                size_bytes   = up.get("size")
                content_type = (up.get("file") or {}).get("mimeType")
                public_url   = create_anonymous_link(item_id)
                thumbnail_url = get_thumbnail_url(item_id)

                # 3) calcular siguiente orden y guardar en BD
                ultimo = (AdjuntoModel.query
                          .filter_by(id_reclamo=id_reclamo)
                          .order_by(AdjuntoModel.orden.desc())
                          .first())
                next_orden = (ultimo.orden + 1) if ultimo else 1

                adj = AdjuntoModel(
                    id_reclamo    = id_reclamo,
                    file_name     = file_name,
                    ruta_imagen   = public_url,
                    drive_item_id = item_id,
                    content_type  = content_type,
                    size_bytes    = size_bytes,
                    orden         = next_orden,
                    thumbnail_url = thumbnail_url,
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

        status = 201 if resultados_ok and not resultados_error else (207 if resultados_ok else 400)
        return jsonify({"ok": bool(resultados_ok), "subidos": resultados_ok, "errores": resultados_error}), status

    except Exception as e:
        db.session.rollback()
        return jsonify({"ok": False, "message": str(e)}), 500