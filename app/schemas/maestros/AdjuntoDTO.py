# app/schemas/adjunto.py
from marshmallow import Schema, fields
from app.models.transacciones import AdjuntoModel

class AdjuntoSchema(Schema):
    id_adjunto   = fields.Int()
    id_reclamo   = fields.Int()
    file_name    = fields.Str()
    ruta_imagen  = fields.Str()
    drive_item_id= fields.Str()
    thumbnail_url= fields.Str(allow_none=True)
    content_type = fields.Str()
    size_bytes   = fields.Int()
    orden        = fields.Int()
    creado_en    = fields.DateTime(allow_none=True)

adjunto_schema  = AdjuntoSchema()
adjuntos_schema = AdjuntoSchema(many=True)
