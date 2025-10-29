from app.extensions import db

class ClienteModel(db.Model):
    __tablename__ = "SA1010"

    cli_id = db.Column("R_E_C_N_O_", db.Integer, primary_key=True)
    cod = db.Column("A1_COD",db.String(15))
    nombre = db.Column("A1_NOME",db.String(80))
    estado = db.Column("A1_MSBLQL",db.String(1))
    delete=db.Column("D_E_L_E_T_",db.String(1))
    loja   = db.Column("A1_LOJA", db.String(2)) 
    telefono   = db.Column("A1_TEL", db.String(15)) 
    email   = db.Column("A1_EMAIL", db.String(80))
    departamento  = db.Column("A1_ESTADO", db.String(20))
    distrito   = db.Column("A1_BAIRRO", db.String(30))
    direccion   = db.Column("A1_END", db.String(60))

