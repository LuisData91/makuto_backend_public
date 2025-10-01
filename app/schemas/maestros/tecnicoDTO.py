from marshmallow import Schema, fields

class TecnicoResponseDTO(Schema):
  
    cod_tec = fields.Str(dump_only=True)
    nombre = fields.Str(dump_only=True)
    estado = fields.Str(dump_only=True)