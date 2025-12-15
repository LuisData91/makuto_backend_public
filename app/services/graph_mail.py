# app/services/graph_mail.py

from typing import Iterable
import requests

# Reutilizamos la autenticación de Graph que ya tienes
from app.services.graph_files import _auth_headers

# Remitente por defecto para todas las notificaciones
DEFAULT_FROM_ADDRESS = "notificaciones@bakels.com.pe"

# Destinatarios fijos (ajusta estos correos reales)
DEFAULT_TO_ADDRESSES = [
    "zoila.saavedra@bakels.com.pe",
    "calidad@bakels.com.pe",
    "alberto.vasquez@bakels.com.pe",
]


def send_mail_graph(
    from_address: str,
    to_addresses: Iterable[str],
    subject: str,
    html_body: str,
    save_to_sent: bool = True,
) -> None:
    """
    Envía un correo usando Microsoft Graph con permiso Mail.Send (Application).

    - from_address: buzón remitente (ej. 'notificaciones@bakels.com.pe')
    - to_addresses: lista/iterable de correos destino
    - subject: asunto del mensaje
    - html_body: cuerpo del mensaje en HTML
    """
    url = f"https://graph.microsoft.com/v1.0/users/{from_address}/sendMail"
    headers = _auth_headers({"Content-Type": "application/json"})

    message = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "HTML",
                "content": html_body,
            },
            "toRecipients": [
                {"emailAddress": {"address": addr}}
                for addr in to_addresses
            ],
        },
        "saveToSentItems": save_to_sent,
    }

    resp = requests.post(url, headers=headers, json=message, timeout=30)
    resp.raise_for_status()  # lanza excepción si falla

def build_reclamo_email_body(
    reclamo_data: dict,
    adjuntos_urls: list[str],
    titulo_banner: str,
) -> str:
    """
    Genera el cuerpo HTML del correo de reclamo (versión COMPACTA).
    """

    # Bloque de adjuntos
    if not adjuntos_urls:
        adjuntos_html = (
            '<p style="margin:2px 0 0;font-size:13px;color:#666;">Sin adjuntos</p>'
        )
    else:
        items = []
        for idx, url in enumerate(adjuntos_urls, start=1):
            items.append(
                f'<li style="margin:0 0 2px 0;">'
                f'<a href="{url}" '
                'style="color:#0b5ed7;text-decoration:none;" target="_blank" '
                f'rel="noopener noreferrer">Adjunto {idx}</a>'
                "</li>"
            )
        adjuntos_html = (
            '<ul style="margin:4px 0 0 18px;padding:0;">'
            + "".join(items) +
            "</ul>"
        )

    num_doc = (
        reclamo_data.get("num_doc", "")
        or reclamo_data.get("documento", "")
    )

    html = f"""
<div style="font-family:'Segoe UI',Arial,sans-serif;font-size:13px;color:#222;line-height:1.35;">
  <div style="max-width:820px;margin:12px auto;border-radius:6px;
              overflow:hidden;border:1px solid #e1e5ea;
              box-shadow:0 1px 3px rgba(15,23,42,.08);">

    <!-- Cabecera -->
    <div style="background:#006d3d;color:#ffffff;
                padding:10px 14px;border-bottom:3px solid #00b894;">
      <div style="display:flex;align-items:center;gap:6px;
                  font-size:16px;font-weight:600;">
        <span>📢</span>
        <span>{titulo_banner}</span>
      </div>
      <div style="margin-top:2px;font-size:12px;opacity:0.9;">
        N° Reclamo: <strong>{num_doc}</strong>
      </div>
    </div>

    <!-- Contenido -->
    <div style="padding:12px 14px;">

      <!-- Fecha emisión -->
      <div style="margin-bottom:8px;font-size:12px;color:#555;display:flex;align-items:center;gap:4px;">
        <span>📅</span>
        <span><strong>Fecha emisión:</strong> {reclamo_data.get("fecha_emision","")}</span>
      </div>

      <!-- Cliente + Producto -->
      <div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:8px;">

        <!-- Cliente -->
        <div style="flex:1 1 260px;background:#f8fafb;border-radius:4px;
                    padding:8px 10px;border:1px solid #e1e5ea;">
          <div style="font-size:13px;font-weight:600;margin-bottom:4px;
                      display:flex;align-items:center;gap:6px;">
            <span>👤</span><span>Cliente</span>
          </div>
          <div style="margin-bottom:2px;"><strong>Nombre:</strong> {reclamo_data.get("cliente","")}</div>
          <div style="margin-bottom:2px;"><strong>Teléfono:</strong> {reclamo_data.get("telefono_cliente","") or "-"}</div>
          <div style="margin-bottom:2px;"><strong>Correo:</strong> {reclamo_data.get("correo_cliente","") or "-"}</div>
          <div><strong>Dirección:</strong> {reclamo_data.get("direccion_cliente","") or "-"}</div>
        </div>

        <!-- Producto -->
        <div style="flex:1 1 260px;background:#f8fafb;border-radius:4px;
                    padding:8px 10px;border:1px solid #e1e5ea;">
          <div style="font-size:13px;font-weight:600;margin-bottom:4px;
                      display:flex;align-items:center;gap:6px;">
            <span>📦</span><span>Producto</span>
          </div>
          <div style="margin-bottom:2px;"><strong>Código:</strong> {reclamo_data.get("cod_prod","")}</div>
          <div style="margin-bottom:2px;"><strong>Nombre:</strong> {reclamo_data.get("nombre_prod","")}</div>
          <div style="margin-bottom:2px;"><strong>Lote:</strong> {reclamo_data.get("lote_prod","")}</div>
          <div><strong>Cantidad reclamada:</strong> {reclamo_data.get("cantidad_reclamada","")}</div>
        </div>

      </div>

      <!-- Despacho -->
      <div style="margin-bottom:8px;background:#fdfdfd;border-radius:4px;
                  padding:6px 10px;border:1px dashed #d0d7de;">
        <div style="font-size:13px;font-weight:600;margin-bottom:2px;
                    display:flex;align-items:center;gap:6px;">
          <span>🚚</span><span>Información de despacho</span>
        </div>
        <div><strong>Fecha despacho:</strong> {reclamo_data.get("fecha_despacho","")}</div>
      </div>

      <!-- Reclamo -->
      <div style="margin-bottom:8px;background:#fff7f0;border-radius:4px;
                  padding:8px 10px;border:1px solid #ffd9b3;">
        <div style="font-size:13px;font-weight:600;margin-bottom:4px;
                    display:flex;align-items:center;gap:6px;">
          <span>⚠️</span><span>Reclamo</span>
        </div>
        <div style="margin-bottom:2px;"><strong>Tipo:</strong> {reclamo_data.get("tipo_reclamo","")}</div>
        <div style="margin-bottom:2px;"><strong>Vendedor:</strong> {reclamo_data.get("nombre_vendedor","")}</div>
        <div style="margin-top:4px;">
          <strong>Descripción:</strong>
          <div style="margin-top:3px;white-space:pre-wrap;">
            {reclamo_data.get("descripcion_reclamo","")}
          </div>
        </div>
      </div>

      <!-- Adjuntos -->
      <div style="margin-bottom:4px;background:#f8fafb;border-radius:4px;
                  padding:8px 10px;border:1px solid #e1e5ea;">
        <div style="font-size:13px;font-weight:600;margin-bottom:4px;
                    display:flex;align-items:center;gap:6px;">
          <span>📎</span><span>Adjuntos</span>
        </div>
        {adjuntos_html}
      </div>

    </div>

    <!-- Pie -->
    <div style="padding:8px 14px 10px 14px;font-size:11px;color:#777;
                border-top:1px solid #e1e5ea;background:#f9fafb;">
      Este correo fue generado automáticamente por el sistema de Solicitud de Reclamos.
      Si tienes alguna consulta, por favor responde al usuario que ingresó el reclamo.
    </div>

  </div>
</div>
"""
    return html.strip()
