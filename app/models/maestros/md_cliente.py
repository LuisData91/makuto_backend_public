from app.extensions import db

class ClienteModel(db.Model):
    __tablename__ = "SA1010"

    cli_id = db.Column("R_E_C_N_O_", db.Integer, primary_key=True)
    cod = db.Column("A1_COD",db.string(15))
    nombre = db.Column("A1_NOME",db.string(80))
    estado = db.Column("A1_MSBLQL",db.string(1))
    delete=db.Column("D_E_L_E_T_",db.Integer)
    

    