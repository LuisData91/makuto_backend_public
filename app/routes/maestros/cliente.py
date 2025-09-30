from flask import Blueprint, request
from app.models.maestros.md_cliente import ClienteModel
from app.schemas.maestros.clienteDTO import ClienteResponseDTO

cliente_bp = Blueprint('cliente', __name__, url_prefix='/cliente')

cliente_output_schema = ClienteResponseDTO()
cliente_output_lista_schema = ClienteResponseDTO(many=True)

@cliente_bp.get("")
def general():
    try:
        clientes = ClienteModel.query.filter(
            ClienteModel.delete == "",
            ClienteModel.estado == "2"
        ).all()

        data = cliente_output_lista_schema.dump(clientes)
        
        return {"message": "Lista de Clientes", "content": data}, 200
    
    except Exception as e:
        return {"message": "Ocurrió un error inesperado", "content": str(e)}, 500

@cliente_bp.get("/<int:idCliente>")
def registro(idCliente: int):
    try:
        cliente = ClienteModel.query.filter(
            ClienteModel.delete == "",
            ClienteModel.cli_id == idCliente
        ).first()

    except Exception as e:
        return {"message": "Ocurrió un error inesperado", "content": str(e)}, 500

    if cliente is None:
        return {"message": "Cliente no encontrado", "content": None}, 404

    return {
        "message": "Cliente encontrado",
        "content": cliente_output_schema.dump(cliente)
    }, 200