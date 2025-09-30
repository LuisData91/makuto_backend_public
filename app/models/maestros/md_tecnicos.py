from app.extensions import db

class TecnicosModel(db.Model):
    __tablename__ = "BKS0087"

    cod_tec = db.Column("ID", db.string(10), primary_key=True)
    nombre = db.Column("NOMBRES",db.string(120))
    estado = db.Column("ESTADO",db.string(1))
    