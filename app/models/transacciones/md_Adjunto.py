# app/models/adjunto.py
# from app.db import db
# from app.extensions import db
from app.db import db

class AdjuntoModel(db.Model):
    __tablename__ = "BKS0092_ADJUNTOS"
    id_adjunto   = db.Column("ID_ADJUNTO", db.Integer, primary_key=True)
    id_reclamo   = db.Column("ID_RECLAMO", db.Integer, nullable=False, index=True)
    file_name    = db.Column("FILE_NAME", db.String(255), nullable=False)
    ruta_imagen  = db.Column("RUTA_IMAGEN", db.String(2000), nullable=False)
    drive_item_id= db.Column("DRIVE_ITEM_ID", db.String(100), nullable=False)
    thumbnail_url= db.Column("THUMBNAIL_URL", db.String(2000))
    content_type = db.Column("CONTENT_TYPE", db.String(100))
    size_bytes   = db.Column("SIZE_BYTES", db.Integer)
    etag         = db.Column("ETAG", db.String(200))
    orden        = db.Column("ORDEN", db.Integer, default=1)
    creado_en    = db.Column("CREADO_EN", db.DateTime)
    
