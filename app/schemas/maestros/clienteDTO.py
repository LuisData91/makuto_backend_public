from marshmallow import Schema, fields

class ClienteResponseDTO(Schema):
    cli_id = fields.Int(dump_only=True)
    cod = fields.Str(dump_only=True)
    nombre = fields.Str(dump_only=True)
    estado = fields.Str(dump_only=True)