from app.extensions import db

class TipoVisitaModel(db.Model):
    __tablename__ = "BKS0088"

    id_visita = db.Column("ID", db.Integer, primary_key=True)
    descripcion = db.Column("DESCRIPCION",db.String(240))
  