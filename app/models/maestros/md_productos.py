from app.extensions import db

class ProductoModel(db.Model):
    __tablename__ = "SB1010"

    prod_id = db.Column("R_E_C_N_O_", db.Integer, primary_key=True)
    cod = db.Column("B1_COD",db.String(15))
    nombre = db.Column("B1_DESC",db.String(60))
    estado = db.Column("B1_MSBLQL",db.String(1))
    delete=db.Column("D_E_L_E_T_",db.String(1))