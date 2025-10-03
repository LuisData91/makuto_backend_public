
from decimal import Decimal
from marshmallow import Schema, fields, validate, post_load, EXCLUDE, validates, ValidationError
from app.models.transacciones.md_cabRegIT import cabRegITModel
from app.models.transacciones.md_det import detModel
    # =================DETALLE REGISTRO DE VISITA ==================
class detCreateRequestDTO(Schema):
    class Meta:
        unknown = EXCLUDE

 
    id_cab = fields.Integer(
        required=True, 
        # strict=True, 
        validate=validate.Range(min=1)
    )

    cod_prod = fields.String(
        required=True, 
        # strict=True, 
        error_messages={
            "required": "El campo Cod producto es obligatorio.",
            "null": "El campo Cod producto no puede ser nulo."
        }
    ) 

    
    @post_load
    def make_model(self, data, **kwargs):
        return detModel(**data)
    

class detUpdateRequestDTO(Schema):
    class Meta:
        unknown = EXCLUDE
     
    id_cab = fields.Integer(
        required=True, 
        strict=True, 
        validate=validate.Range(min=1)
    )

    cod_prod = fields.String(
        required=True, 
        # strict=True, 
        error_messages={
            "required": "El campo Cod producto es obligatorio.",
            "null": "El campo Cod producto no puede ser nulo."
        }
    ) 
class detResponseDTO(Schema):
    id = fields.Int(dump_only=True)
    cod_prod = fields.Str(dump_only=True)


# =================CABECERA REGISTRO DE VISITA ==================

class cabRegITCreateRequestDTO(Schema):
    class Meta:
        unknown = EXCLUDE

    # id = fields.Integer(
    #     required=True, 
    #     strict=True, 
    #     validate=validate.Range(min=1)
    # )

    fecha_dig = fields.String(
        required=True, 
        # strict=True, 
        error_messages={
            "required": "El campo Fecha es obligatorio.",
            "null": "El campo Fecha no puede ser nulo."
        }
    )

    id_tec = fields.String(
        required=True, 
        # strict=True, 
        validate=validate.Length(min=1)
    )

    id_vend = fields.String(
        required=True, 
        # strict=True, 
        validate=validate.Length(min=1)
    )
    id_clien = fields.String(
        required=True, 
        # strict=True, 
        validate=validate.Length(min=1)
    )
    id_motivo = fields.Integer(
        required=True, 
        # strict=True, 
        validate=validate.Range(min=1)
    )
    correlativo = fields.String(
        required=True, 
        # strict=True, 
        error_messages={
            "required": "El campo Fecha es obligatorio.",
            "null": "El campo Fecha no puede ser nulo."
        }
    )
    @post_load
    def make_model(self, data, **kwargs):
        return cabRegITModel(**data)

class cabRegITUpdateRequestDTO(Schema):
    class Meta:
        unknown = EXCLUDE
 
    fecha_dig = fields.String(
        required=True, 
        # strict=True, 
        error_messages={
            "required": "El campo Fecha es obligatorio.",
            "null": "El campo Fecha no puede ser nulo."
        }
    )

    id_tec = fields.String(
        required=True, 
        # strict=True, 
        validate=validate.Length(min=1)
    )

    id_vend = fields.String(
        required=True, 
        # strict=True, 
        validate=validate.Length(min=1)
    )
    id_clien = fields.String(
        required=True, 
        # strict=True, 
        validate=validate.Length(min=1)
    )
    id_motivo = fields.Integer(
        required=True, 
        # strict=True, 
        validate=validate.Range(min=1)
    )
    correlativo = fields.String(
        required=True, 
        # strict=True, 
        error_messages={
            "required": "El campo Fecha es obligatorio.",
            "null": "El campo Fecha no puede ser nulo."
        }
    )    

class cabRegITResponseDTO(Schema):
    id = fields.Int(dump_only=True)
    fecha_dig = fields.Str(dump_only=True)
    id_tec = fields.Str(dump_only=True)    
    id_vend = fields.Str(dump_only=True)    
    id_clien = fields.Str(dump_only=True)   
    id_motivo = fields.Int(dump_only=True)
    correlativo = fields.Str(dump_only=True)


    