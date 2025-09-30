from app.extensions import db

class VendedorModel(db.Model):
    __tablename__ = "SA3010"

    vend_id = db.Column("R_E_C_N_O_", db.Integer, primary_key=True)
    cod = db.Column("A3_COD",db.String(6))
    nombre = db.Column("A3_NOME",db.String(40))
    estado = db.Column("A3_MSBLQL",db.String(1))
    delete=db.Column("D_E_L_E_T_",db.String(1))