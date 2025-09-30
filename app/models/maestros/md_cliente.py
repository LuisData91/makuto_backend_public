from app.extensions import db

class ClienteModel(db.Model):
    __tablename__ = "Cliente"

    cli_id = db.Column("R_E_C_N_O_", db.Integer, primary_key=True)