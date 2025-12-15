# app/utils/usuario_actual.py
from flask import request

def get_usuario_actual_id():
    """
    Obtiene el USR_ID del usuario desde el header.
    Lánzale una excepción o devuelve None si no viene.
    """
    usr_id = request.headers.get("X-User-Id")
    return usr_id
