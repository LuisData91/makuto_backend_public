from marshmallow import Schema, fields

class EmpleadoResponseDTO(Schema):
    empleado_id = fields.Int(dump_only=True)
    nombres = fields.Str(dump_only=True)
    dni = fields.Str(dump_only=True)
    