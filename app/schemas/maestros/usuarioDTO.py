from marshmallow import Schema, fields

class UsuarioResponseDTO(Schema):
    usr_cod = fields.String()
    usr_usu = fields.String()
    usr_nom = fields.String()
    usr_id = fields.Integer()