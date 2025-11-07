from marshmallow import Schema, fields, validate    

from app.models.transacciones import SolicitudReclamoModel

class SolicitudReclamoResponseDTO(Schema):

    fecha_emision = fields.Str(dump_only=True)
    documento = fields.Str(dump_only=True)
    cod_prod = fields.Str(dump_only=True)
    nombre_prod = fields.Str(dump_only=True)
    lote_prod = fields.Str(dump_only=True)   
    cantidad_reclamada = fields.Int(dump_only=True)
    cliente = fields.Str(dump_only=True)
    telefono_cliente = fields.Str(dump_only=True)
    correo_cliente = fields.Str(dump_only=True)
    direccion_cliente = fields.Str(dump_only=True)
    fecha_despacho = fields.Str(dump_only=True)
    tipo_reclamo = fields.Str(dump_only=True)
    descripcion_reclamo = fields.Str(dump_only=True)
    nombre_vendedor = fields.Str(dump_only=True)
    ruta_imagen = fields.Str(dump_only=True)
    
    
 

class ReclamoCreateRequestDTO(Schema):
    fecha_emision = fields.Str(
        required=True,
    )

    documento = fields.Str(
        required=False,
    )

    cod_prod = fields.Str(
        required=True,
   )

    nombre_prod = fields.Str(
        required=True,

    )

    lote_prod = fields.Str(
        required=True,

    )

    cantidad_reclamada = fields.Int(
        required=True,
    )

    cliente = fields.Str(
        required=True,
    )

    telefono_cliente = fields.Str(
        required=False,

    )

    correo_cliente = fields.Str(
        required=False,
    )

    direccion_cliente = fields.Str(
        required=False,

    )

    fecha_despacho = fields.Str(
        required=True,
    )

    tipo_reclamo = fields.Str(
        required=True,
    )

    descripcion_reclamo = fields.Str(
        required=True,
    )

    nombre_vendedor = fields.Str(
        required=True,
    )

    ruta_imagen = fields.Str(
        required=True,
    )

    
    

class ReclamoUpdateRequestDTO(Schema):
    fecha_emision = fields.Str(
        required=False,
    )

    documento = fields.Str(
        required=False,
    )

    cod_prod = fields.Str(
        required=False,
    )

    nombre_prod = fields.Str(
        required=False,
    )

    lote_prod = fields.Str(
        required=False,
    )

    cantidad_reclamada = fields.Int(
        required=False,
    )

    cliente = fields.Str(
        required=False,
    )

    telefono_cliente = fields.Str(
        required=False,
    )

    correo_cliente = fields.Str(
        required=False,
    )

    direccion_cliente = fields.Str(
        required=False,
    )

    fecha_despacho = fields.Str(
        required=False,
    )

    tipo_reclamo = fields.Str(
        required=False,
    )

    descripcion_reclamo = fields.Str(
        required=False,
    )

    nombre_vendedor = fields.Str(
        required=False,
    )

    ruta_imagen = fields.Str(
        required=False,
    )
