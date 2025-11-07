import os
import time
import requests
import math 

# -------- Credenciales (desde .env) --------
TENANT_ID = os.getenv("MS_TENANT_ID")
CLIENT_ID = os.getenv("MS_CLIENT_ID")
CLIENT_SECRET = os.getenv("MS_CLIENT_SECRET")
SCOPE = "https://graph.microsoft.com/.default"

# -------- IDs reales de tu sitio --------
DRIVE_ID = "b!fOYpbN9m8kC6uO-V12b-wQVE_BOc321HoPKY9Q2lSS5GBrX2sFZNR4a0ShAlnk1r"
FOLDER_ID = "017FBTP536XGZPMKIEFJGKFTRY4SKM5C4A"  # carpeta Adjuntos_Calidad                                 # Adjuntos_Calidad

# ---------- Cache simple de token ----------
_token_cache = {"access_token": None, "exp": 0}

def _get_token() -> str:
    """Obtiene y cachea un token de Microsoft Graph."""
    now = time.time()
    if _token_cache["access_token"] and now < _token_cache["exp"] - 60:
        return _token_cache["access_token"]

    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": SCOPE,
        "grant_type": "client_credentials",
    }
    r = requests.post(url, data=data)
    r.raise_for_status()
    token_data = r.json()
    _token_cache["access_token"] = token_data["access_token"]
    _token_cache["exp"] = now + token_data.get("expires_in", 3600)
    return _token_cache["access_token"]

def _auth_headers(extra: dict | None = None) -> dict:
    h = {"Authorization": f"Bearer {_get_token()}"}
    if extra:
        h.update(extra)
    return h

# ---------- SUBIDA SIMPLE (≤ 4 MB) ----------
def upload_small(file_bytes: bytes, file_name: str) -> dict:
    """
    Sube un archivo a la carpeta Adjuntos_Calidad.
    Devuelve el driveItem (id, name, size, file.mimeType, etc.).
    """
    url = (f"https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}"
           f"/items/{FOLDER_ID}:/{file_name}:/content?nameConflictBehavior=rename")
    headers = _auth_headers({"Content-Type": "application/octet-stream"})
    r = requests.put(url, headers=headers, data=file_bytes, timeout=60)
    r.raise_for_status()
    return r.json()

# ---------- CREAR LINK PÚBLICO ----------
def create_anonymous_link(item_id: str) -> str:
    """
    Crea un link 'Anyone – view' y devuelve link.webUrl.
    """
    url = f"https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}/items/{item_id}/createLink"
    headers = _auth_headers({"Content-Type": "application/json"})
    body = {"type": "view", "scope": "anonymous"}
    r = requests.post(url, headers=headers, json=body, timeout=25)
    r.raise_for_status()
    return r.json()["link"]["webUrl"]

# ---------- MINIATURA (opcional) ----------
def get_thumbnail_url(item_id: str, size: str = "medium") -> str | None:
    url = f"https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}/items/{item_id}/thumbnails"
    r = requests.get(url, headers=_auth_headers(), timeout=20)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    arr = r.json().get("value") or []
    if not arr:
        return None
    sizes = arr[0]
    if size == "large":
        return sizes.get("large", {}).get("url")
    if size == "small":
        return sizes.get("small", {}).get("url")
    return sizes.get("medium", {}).get("url")

# -------------SUBIDA GRANDE (> 4 MB) -------------
def _create_upload_session(file_name: str) -> str:
    """
    Crea una sesión de subida para un archivo dentro de la carpeta destino.
    Devuelve el uploadUrl (pre-signed) donde enviaremos los chunks.
    """
    url = (
        f"https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}"
        f"/items/{FOLDER_ID}:/{file_name}:/createUploadSession"
    )
    body = {
        "@microsoft.graph.conflictBehavior": "rename",
        "deferCommit": False,
    }
    r = requests.post(url, headers=_auth_headers({"Content-Type": "application/json"}), json=body, timeout=25)
    r.raise_for_status()
    return r.json()["uploadUrl"]

def upload_large_stream(fileobj, file_name: str, chunk_mb: int = None) -> dict:
    """
    Sube archivos grandes usando upload session, leyendo desde fileobj (FileStorage.stream).
    Devuelve el driveItem JSON.
    """
    if chunk_mb is None:
        chunk_mb = int(os.getenv("SP_UPLOAD_CHUNK_MB", "8"))
    chunk_size = chunk_mb * 1024 * 1024

    # calcular tamaño total
    try:
        cur = fileobj.tell()
    except Exception:
        cur = 0
    try:
        fileobj.seek(0, os.SEEK_END)
        total = fileobj.tell()
        fileobj.seek(0)
    except Exception:
        # si no es seekable, leemos a memoria solo para medir (raro en FileStorage)
        data = fileobj.read()
        total = len(data)
        from io import BytesIO
        fileobj = BytesIO(data)

    upload_url = _create_upload_session(file_name)

    start = 0
    final_resp = None
    while start < total:
        to_read = min(chunk_size, total - start)
        chunk = fileobj.read(to_read)
        end = start + len(chunk) - 1

        headers = {
            "Content-Length": str(len(chunk)),
            "Content-Range": f"bytes {start}-{end}/{total}",
        }
        resp = requests.put(upload_url, headers=headers, data=chunk, timeout=120)
        # 202/201 cuando falta; 200 (OK) cuando termina y devuelve el driveItem
        if resp.status_code not in (200, 201, 202):
            resp.raise_for_status()
        final_resp = resp
        start = end + 1

    return final_resp.json()  # driveItem (id, name, size, file.mimeType, ...)

# app/services/graph_files.py
def get_thumbnail_url(item_id: str, size: str = "medium") -> str | None:
    """
    Devuelve una URL temporal de miniatura generada por Graph.
    Tamaños disponibles en OneDrive/SharePoint: small / medium / large.
    Retorna None si el item no tiene miniaturas aún.
    """
    url = f"https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}/items/{item_id}/thumbnails"
    r = requests.get(url, headers=_auth_headers(), timeout=20)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    arr = r.json().get("value") or []
    if not arr:
        return None
    sizes = arr[0]  # primera colección
    if size == "small":
        return (sizes.get("small") or {}).get("url")
    if size == "large":
        return (sizes.get("large") or {}).get("url")
    return (sizes.get("medium") or {}).get("url")
