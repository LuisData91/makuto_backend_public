from app.extensions import db
from sqlalchemy.orm import relationship, foreign


class TecnicosModel(db.Model):
    __tablename__ = "BKS0087"

    cod_tec = db.Column("ID", db.String(10), primary_key=True)
    nombre = db.Column("NOMBRES", db.String(120))
    estado = db.Column("ESTADO", db.String(1), default="1")
    userid = db.Column("IDUSUARIO", db.String(6))

    user = relationship(
        "Usuario",
        primaryjoin="foreign(TecnicosModel.userid) == Usuario.usr_cod",
        viewonly=True,  # no intentamos escribir a través de esta relación
        lazy="joined",  # eager load por join
        uselist=False,
    )
