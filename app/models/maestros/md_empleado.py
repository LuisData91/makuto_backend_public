from app.extensions import db

class EmpleadoModel(db.Model):
    __tablename__ = "SRA010"

    id = db.Column("R_E_C_N_O_", db.Integer, primary_key=True)
    empleado_id = db.Column("RA_MAT", db.String(20))
    nombres = db.Column("RA_NOMECMP",db.String(70))
    gen = db.Column("RA_SEXO",db.String(40))
    dni = db.Column("RA_CIC",db.String(15))
    delete=db.Column("D_E_L_E_T_",db.String(1))
    f_baja=db.Column("RA_DEMISSA",db.String(8))