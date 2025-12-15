# test_mail_reclamo.py

import os
from dotenv import load_dotenv  # asegúrate de tener python-dotenv instalado

# 1) Cargar variables de entorno desde .env
BASE_DIR = os.path.dirname(__file__)
dotenv_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path)

# 2) Recién después importamos graph_mail (que usa os.getenv)
from app.services.graph_mail import (
    send_mail_graph,
    build_reclamo_email_body,
    DEFAULT_FROM_ADDRESS,
)

TEST_TO_ADDRESSES = [
    
    "zoila.saavedra@bakels.com.pe",
    "calidad@bakels.com.pe",
    "alberto.vasquez@bakels.com.pe",  
]


def main():
    reclamo_data = {
        "id_reclamo": 9999,
        "fecha_registro": "2025-11-18",
        "cliente": "CLIENTE DE PRUEBA",
        "contacto": "Contacto Prueba",
        "canal": "Formulario Web",
        "producto": "Producto X",
        "tipo_reclamo": "Calidad",
        "descripcion": "Este es un reclamo de prueba generado desde el script.",
        "usuario_registra": "ÁREA DE SISTEMAS",
    }

    adjuntos_urls = [
        "https://example.com/adjunto1",
        "https://example.com/adjunto2",
    ]

    html_body = build_reclamo_email_body(reclamo_data, adjuntos_urls)
    subject = f"[PRUEBA] Nuevo reclamo N° {reclamo_data['id_reclamo']}"

    print("Enviando correo de prueba...")
    send_mail_graph(
        from_address=DEFAULT_FROM_ADDRESS,
        to_addresses=TEST_TO_ADDRESSES,
        subject=subject,
        html_body=html_body,
        save_to_sent=True,
    )
    print("Correo enviado correctamente.")


if __name__ == "__main__":
    main()
