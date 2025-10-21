from sqlalchemy import text

def next_correlativo_mssql(session, prefijo="FV"):
    sql = text("""
        DECLARE @out varchar(20);
        EXEC dbo.sp_next_correlativo :prefijo, @out OUTPUT;
        SELECT @out AS correlativo;
    """)
    row = session.execute(sql, {"prefijo": prefijo}).fetchone()
    # row[0] o row.correlativo, según el driver
    return row[0] if row is not None else None