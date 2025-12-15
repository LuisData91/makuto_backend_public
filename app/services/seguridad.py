from sqlalchemy import text
from app.extensions import db
from app.models.maestros.md_usuarios import Usuario

CALIDAD_GROUP_ID = "000006"

def es_usuario_calidad_por_id(usr_id: str) -> bool:
    """
    Retorna True si el usuario pertenece al grupo de Calidad (000006).
    Usa los grupos obtenidos por obtener_grupos_usuario.
    """
    grupos = obtener_grupos_usuario(usr_id)
    return any(g["gr_id"] == CALIDAD_GROUP_ID for g in grupos)
def obtener_usr_cod_por_recno(recno: str) -> str | None:
    """
    Dado el R_E_C_N_O_ (usr_id interno, ej. 101),
    devuelve el USR_ID real de Protheus (ej. '000105').
    """
    try:
        recno_int = int(recno)
    except (TypeError, ValueError):
        return None

    usuario = (
        Usuario.query
        .filter(
            Usuario.usr_id == recno_int,   # R_E_C_N_O_
            Usuario.usr_del == ''          # D_E_L_E_T_ filtro lógico
        )
        .first()
    )

    return usuario.usr_cod if usuario else None  # USR_ID ('000105')

def obtener_grupos_usuario(usr_id: str):
    """
    Devuelve una lista de diccionarios con los grupos a los que pertenece el usuario.
    """
    sql = text("""
        SELECT
            GRP.GR__ID,
            GRP.GR__CODIGO,
            GRP.GR__NOME
        FROM SYS_USR USR
        LEFT JOIN SYS_USR_GROUPS GRPUSER ON GRPUSER.USR_ID = USR.USR_ID
        LEFT JOIN SYS_GRP_GROUP GRP ON GRP.GR__ID = GRPUSER.USR_GRUPO
        WHERE USR.D_E_L_E_T_ = ''
          AND GRPUSER.D_E_L_E_T_ = ''
          AND GRP.D_E_L_E_T_ = ''
          AND USR.USR_MSBLQL = '2'
          AND USR.USR_ID = :usr_id
    """)

    rows = db.session.execute(sql, {"usr_id": usr_id}).fetchall()

    return [
        {
            "gr_id": r.GR__ID,
            "gr_codigo": r.GR__CODIGO,
            "gr_nombre": r.GR__NOME,
        }
        for r in rows
    ]
