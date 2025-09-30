from marshmallow import Schema, fields

class ClienteResponseDTO(Schema):
    id = fields.Int(dump_only=True)
    empresa_cod = fields.Str(dump_only=True)
    empresa_nom = fields.Str(dump_only=True)
    empresa_act = fields.Bool(dump_only=True)