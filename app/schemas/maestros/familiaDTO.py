from marshmallow import Schema, fields

class FamiliaResponseDTO(Schema):
    id_fam = fields.Int(dump_only=True)
    cod = fields.Str(dump_only=True)
    descripcion = fields.Str(dump_only=True)
    