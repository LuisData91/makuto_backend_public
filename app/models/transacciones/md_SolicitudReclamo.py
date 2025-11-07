from app.extensions import db

class SolicitudReclamoModel(db.Model):
    __tablename__ = "BKS0092"

    id = db.Column("ID", db.Integer, primary_key=True) 
    fecha_emision      = db.Column("FECHA_EMISION", db.String(10),  nullable=False)
    documento      = db.Column("NUM_DOC", db.String(20),  nullable=False)
    cod_prod           = db.Column("COD_PROD", db.String(15),       nullable=False, index=True)
    nombre_prod        = db.Column("NOMBRE_PROD", db.String(60),    nullable=False)
    lote_prod          = db.Column("LOTE_PROD", db.String(20),      nullable=False)
    cantidad_reclamada = db.Column("CANTIDAD_RECLAMADA", db.Integer,nullable=False)
    cliente            = db.Column("CLIENTE", db.String(80),        nullable=False, index=True)
    telefono_cliente   = db.Column("TELEFONO_CLIENTE", db.String(15), nullable=False)
    correo_cliente     = db.Column("CORREO_CLIENTE", db.String(80),   nullable=False)
    direccion_cliente  = db.Column("DIRECCION_CLIENTE", db.String(500), nullable=False)
    fecha_despacho     = db.Column("FECHA_DESPACHO", db.String(10),    nullable=False)
    tipo_reclamo       = db.Column("TIPO_RECLAMO", db.String(100),     nullable=False)
    descripcion_reclamo= db.Column("DESCRIPCION_RECLAMO", db.String(900), nullable=False)
    nombre_vendedor    = db.Column("NOMBRE_VENDEDOR", db.String(40),     nullable=False)
    ruta_imagen        = db.Column("RUTA_IMAGEN", db.String(300),        nullable=False)
    estado             = db.Column("ESTADO",db.Integer, default=1)
    fecha_mod          = db.Column(db.DateTime, server_default=db.func.current_timestamp(), name='FECHA_UPDATE')
    
