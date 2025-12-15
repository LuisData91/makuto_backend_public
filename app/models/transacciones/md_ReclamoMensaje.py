# app/models/transacciones/md_ReclamoMensaje.py

from app.extensions import db
from datetime import datetime

class ReclamoMensajeModel(db.Model):
    __tablename__ = "BKS0092MSJ"

    id_mensaje = db.Column("ID_MENSAJE", db.Integer, primary_key=True, autoincrement=True)
    id_reclamo = db.Column("ID_RECLAMO", db.Integer, db.ForeignKey("BKS0092.ID"), nullable=False)
    id_usuario = db.Column("ID_USUARIO", db.Integer, nullable=False)
    mensaje = db.Column("MENSAJE", db.Text, nullable=False)
    fecha_envio = db.Column("FECHA_ENVIO", db.DateTime, default=datetime.now, nullable=False)
    leido = db.Column("LEIDO", db.Boolean, default=False, nullable=False)

    # Relación inversa: un mensaje pertenece a un reclamo
    reclamo = db.relationship("SolicitudReclamoModel", back_populates="mensajes")

    def __repr__(self):
        return f"<ReclamoMensaje {self.id_mensaje} - Reclamo {self.id_reclamo}>"
