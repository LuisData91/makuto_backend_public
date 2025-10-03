from app.extensions import db

class TecnicosModel(db.Model):
    __tablename__ = "BKS0087"

    cod_tec = db.Column("ID", db.String(10), primary_key=True)
    nombre = db.Column("NOMBRES",db.String(120))
    estado = db.Column("ESTADO",db.String(1),default='1')
    