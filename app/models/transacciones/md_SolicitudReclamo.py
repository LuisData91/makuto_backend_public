from app.extensions import db

class SolicitudReclamoModel(db.Model):
    __tablename__ = "BKS0092"

    id = db.Column("ID", db.Integer, primary_key=True) 
    fecha_emision      = db.Column("FECHA_EMISION", db.String(10),  nullable=False)
    documento          = db.Column("NUM_DOC", db.String(20),  nullable=False)
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
    descripcion_reclamo= db.Column("DESCRIPCION_RECLAMO", db.Text, nullable=True)
    nombre_vendedor    = db.Column("NOMBRE_VENDEDOR", db.String(40),     nullable=False)
    ruta_imagen        = db.Column("RUTA_IMAGEN", db.String(300),        nullable=False)
    estado             = db.Column("ESTADO",db.Integer, default=1)  # 1=Pend., 2=Proceso, 3=Cerrado
    fecha_mod          = db.Column(db.DateTime, server_default=db.func.current_timestamp(), name='FECHA_UPDATE')
    id_usuario_registro = db.Column("ID_USUARIO",db.Integer, nullable=False)

    respuesta_calidad = db.Column('RESPUESTA_CALIDAD', db.Text)
    id_usuario_calidad = db.Column('ID_USUARIO_CALIDAD', db.Integer)
    fecha_cierre = db.Column('FECHA_CIERRE', db.String(10))

    # Dentro de SolicitudReclamoModel

    mensajes = db.relationship("ReclamoMensajeModel",back_populates="reclamo",lazy=True,cascade="all, delete-orphan")


  # Constantes de estado (solo a nivel de código)
    ESTADO_ELIMINADO = 0
    ESTADO_PENDIENTE = 1
    ESTADO_EN_PROCESO = 2
    ESTADO_CERRADO = 3
    
