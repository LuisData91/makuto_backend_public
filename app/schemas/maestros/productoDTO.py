from marshmallow import Schema, fields

class ProductoResponseDTO(Schema):
    prod_id = fields.Int(dump_only=True)
    cod = fields.Str(dump_only=True)
    nombre = fields.Str(dump_only=True)
    