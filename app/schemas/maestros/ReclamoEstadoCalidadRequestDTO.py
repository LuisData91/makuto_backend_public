# app/schemas/maestros/ReclamoEstadoCalidadRequestDTO.py

from marshmallow import Schema, fields

class ReclamoEstadoCalidadRequestDTO(Schema):
    estado = fields.Int(required=True)
    respuesta_calidad = fields.String(allow_none=True)
    id_usuario_calidad = fields.Int(required=True)
