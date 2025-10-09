from app.extensions import db

class Usuario(db.Model):
    __tablename__ = 'SYS_USR'
    usr_cod = db.Column("USR_ID", db.String(6))
    usr_usu = db.Column("USR_CODIGO", db.String(25))
    usr_nom = db.Column("USR_NOME", db.String(40))
    usr_del = db.Column("D_E_L_E_T_", db.String(1))
    usr_id = db.Column("R_E_C_N_O_", db.Integer, primary_key=True)