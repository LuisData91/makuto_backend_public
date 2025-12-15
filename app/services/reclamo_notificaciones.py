# app/services/reclamo_notificaciones.py

from typing import List, Optional
from sqlalchemy import text
from flask import current_app

from app.extensions import db
from app.models.transacciones.md_SolicitudReclamo import SolicitudReclamoModel
from app.models.transacciones import AdjuntoModel
from app.services.graph_mail import (
    send_mail_graph,
    build_reclamo_email_body,
    DEFAULT_FROM_ADDRESS,
    DEFAULT_TO_ADDRESSES,
)


def _obtener_reclamo_db(id_reclamo: int) -> Optional[dict]:
    """
    Lee la cabecera del reclamo desde la tabla de SolicitudReclamoModel (BKS0092).
    Devuelve un dict con los campos necesarios para el correo.
    """

    table = SolicitudReclamoModel.__tablename__  # debería ser BKS0092

    sql = text(f"""
        SELECT 
            ID,
            FECHA_EMISION,
            COD_PROD,
            NOMBRE_PROD,
            LOTE_PROD,
            CANTIDAD_RECLAMADA,
            CLIENTE,
            TELEFONO_CLIENTE,
            CORREO_CLIENTE,
            DIRECCION_CLIENTE,
            FECHA_DESPACHO,
            TIPO_RECLAMO,
            DESCRIPCION_RECLAMO,
            NOMBRE_VENDEDOR,
            NUM_DOC,
            ESTADO,
            FECHA_UPDATE
        FROM {table}
        WHERE ID = :id_reclamo
    """)

    row = db.session.execute(sql, {"id_reclamo": id_reclamo}).mappings().first()
    if not row:
        return None

    reclamo_data = {
        "id_reclamo": row["ID"],
        "fecha_emision": row["FECHA_EMISION"],
        "cliente": row["CLIENTE"],
        "telefono_cliente": row["TELEFONO_CLIENTE"],
        "correo_cliente": row["CORREO_CLIENTE"],
        "direccion_cliente": row["DIRECCION_CLIENTE"],
        "cod_prod": row["COD_PROD"],
        "nombre_prod": row["NOMBRE_PROD"],
        "lote": row["LOTE_PROD"],
        "cantidad_reclamada": row["CANTIDAD_RECLAMADA"],
        "fecha_despacho": row["FECHA_DESPACHO"],
        "tipo_reclamo": row["TIPO_RECLAMO"],
        "descripcion": row["DESCRIPCION_RECLAMO"],
        "nombre_vendedor": row["NOMBRE_VENDEDOR"],
        "num_doc": row["NUM_DOC"],
    }

    return reclamo_data


def _obtener_adjuntos_urls(id_reclamo: int) -> List[str]:
    """
    Lee las URLs de SharePoint desde la tabla de adjuntos (BKS0092_ADJUNTOS).
    Usa la columna RUTA_IMAGEN.
    """
    table_adj = AdjuntoModel.__tablename__  # debería ser BKS0092_ADJUNTOS

    sql = text(f"""
        SELECT 
            RUTA_IMAGEN
        FROM {table_adj}
        WHERE ID_RECLAMO = :id_reclamo
        ORDER BY ORDEN, ID_ADJUNTO
    """)

    rows = db.session.execute(sql, {"id_reclamo": id_reclamo}).mappings().all()
    return [r["RUTA_IMAGEN"] for r in rows if r["RUTA_IMAGEN"]]


def notify_reclamo_creado(id_reclamo: int) -> None:
    """
    Orquesta todo:
    - Obtiene datos del reclamo
    - Obtiene URLs de adjuntos
    - Arma el HTML
    - Envía el correo a los destinatarios configurados
    """

    reclamo_data = _obtener_reclamo_db(id_reclamo)
    if not reclamo_data:
        current_app.logger.warning(
            f"[notify_reclamo_creado] Reclamo ID={id_reclamo} no encontrado"
        )
        return

    adjuntos_urls = _obtener_adjuntos_urls(id_reclamo)
    html_body = build_reclamo_email_body(reclamo_data, adjuntos_urls)

    subject = (
        f"Nuevo reclamo N° {reclamo_data['num_doc']} - "
        f"{reclamo_data.get('cliente', '')}"
    )

    try:
        send_mail_graph(
            from_address=DEFAULT_FROM_ADDRESS,
            to_addresses=DEFAULT_TO_ADDRESSES,
            subject=subject,
            html_body=html_body,
            save_to_sent=True,
        )
        current_app.logger.info(
            f"[notify_reclamo_creado] Notificación enviada para reclamo ID={id_reclamo}"
        )
    except Exception as e:
        # Importante: no romper el flujo del backend si el correo falla
        current_app.logger.exception(
            f"[notify_reclamo_creado] Error enviando correo para reclamo ID={id_reclamo}: {e}"
        )
