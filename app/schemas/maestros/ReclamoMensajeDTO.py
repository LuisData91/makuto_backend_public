# app/schemas/maestros/ReclamoMensajeDTO.py

from marshmallow import Schema, fields, validate

class ReclamoMensajeCreateRequestDTO(Schema):
    id_usuario = fields.Int(required=True)
    mensaje = fields.String(
        required=True,
        validate=validate.Length(min=1),
        error_messages={
            "required": "El mensaje es obligatorio."
        }
    )



class ReclamoMensajeResponseDTO(Schema):
    """
    DTO para responder al frontend con la info del mensaje.
    """
    id_mensaje = fields.Int()
    id_reclamo = fields.Int()
    id_usuario = fields.Int()
    
    # Este campo lo puedes completar haciendo join con tu tabla de usuarios
    # en el endpoint (opcional pero muy útil para el chat).
    nombre_usuario = fields.String(allow_none=True)

    mensaje = fields.String()
    fecha_envio = fields.DateTime()
    leido = fields.Boolean()
