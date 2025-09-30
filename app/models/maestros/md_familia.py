from app.extensions import db

class FamiliaModel(db.Model):
    __tablename__ = "SBM010"

    id_fam= db.Column("R_E_C_N_O_", db.Integer, primary_key=True)
    cod = db.Column("BM_GRUPO",db.String(4))
    descripcion = db.Column("BM_DESC",db.String(30))
    delete=db.Column("D_E_L_E_T_",db.String(1))