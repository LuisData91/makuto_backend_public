from app.extensions import db

class cabRegITModel(db.Model):
    __tablename__ = "BKS0089"

    id = db.Column("IDCAB", db.Integer, primary_key=True)
    fecha_dig = db.Column("FECHA_DIG",db.String(10))
    fecha_mod = db.Column("FECHA_MOD", db.DateTime)
    id_tec = db.Column("ID_TEC",db.String(10))
    id_vend = db.Column("ID_VEND",db.String(6))
    id_clien = db.Column("ID_CLIEN",db.String(15))
    id_motivo = db.Column("ID_MOTIVO",db.Integer)
    estado = db.Column("ESTADO",db.Integer)
    
  