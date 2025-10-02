from marshmallow import Schema,fields,validate,post_load,EXCLUDE
from app.models.maestros.md_tecnicos import TecnicosModel



class TecnicoResponseDTO(Schema):
  
    cod_tec = fields.Str(dump_only=True)
    nombre = fields.Str(dump_only=True)
    estado = fields.Str(dump_only=True)



ALLOWED_TIPOS = ("ENT", "SAL", "TRA")
       
class TecnicoCreateRequestDTO(Schema):
    class Meta:
        unknown = EXCLUDE

 

    cod_tec = fields.String(
        required=True,
        error_messages={
            "required": "El campo código es obligatorio.",
            "null": "El campo código no puede ser nulo."
        }
    )

    nombre = fields.String(
        required=True,
        error_messages={
            "required": "El campo nombre es obligatorio.",
            "null": "El campo nombre de serie no puede ser nulo."
        }
    )

    

    @post_load
    def make_model(self, data, **kwargs):
        return TecnicosModel(**data)
    
class TecnicoUpdateRequestDTO(Schema):
    class Meta:
        unknown = EXCLUDE  

    cod_tec = fields.String(
        required=True,
        error_messages={
            "required": "El campo código es obligatorio.",
            "null": "El campo código no puede ser nulo."
        }
    )

    nombre = fields.String(
        required=True,
        error_messages={
            "required": "El campo nombre es obligatorio.",
            "null": "El campo nombre de serie no puede ser nulo."
        }

            
    )

    estado = fields.String(
        required=False,
        error_messages={
            "required": "El campo estado no es obligatorio.",
            "null": "El campo estado   puede ser nulo."
        }

            
    )


  
