from app.extensions import db

class detModel(db.Model):
    __tablename__ = "BKS0090"

    id = db.Column("IDDET", db.Integer, primary_key=True)
    id_cab = db.Column("IDCAB",db.Integer)
    cod_prod = db.Column("ID_PROD",db.String(15))
    estado = db.Column("ESTADO",db.Integer)