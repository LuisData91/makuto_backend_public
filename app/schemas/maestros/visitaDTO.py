from marshmallow import Schema, fields

class VisitaResponseDTO(Schema):
    id_visita = fields.Int(dump_only=True)
    descripcion = fields.Str(dump_only=True)
   