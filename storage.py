import json
import os
from crypto_utils import cargar_clave, cifrar_dato, descifrar_dato

DATA_FILE = "data.json"

def _cargar_data() -> dict:
    """
    Retorna todo el contenido de data.json como dict.
    Si no existe, devuelve {}.
    """
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    else:
        return {}

def _guardar_data(data: dict) -> None:
    """
    Sobrescribe data.json con el dict dado.
    """
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def guardar_credencial(username: str, servicio: str, usuario: str, clave: str) -> None:
    """
    Guarda (o actualiza) la credencial del usuario:
      data.json[username][servicio] = { usuario: <cifrado>, clave: <cifrado> }
    """
    data = _cargar_data()
    user_lower = username.lower()
    if user_lower not in data:
        data[user_lower] = {}

    clave_maestra = cargar_clave()
    entry = {
        "usuario": cifrar_dato(usuario, clave_maestra),
        "clave": cifrar_dato(clave, clave_maestra)
    }

    data[user_lower][servicio.lower()] = entry
    _guardar_data(data)

def leer_credencial(username: str, servicio: str) -> tuple:
    """
    Busca en data.json la credencial de (username, servicio).
    Si existe, devuelve (usuario, clave) descifrados.
    Si no existe, devuelve (None, None).
    """
    data = _cargar_data()
    user_lower = username.lower()
    svc = servicio.lower()

    if user_lower not in data:
        return (None, None)

    entry = data[user_lower].get(svc)
    if not entry:
        return (None, None)

    clave_maestra = cargar_clave()
    try:
        usuario = descifrar_dato(entry["usuario"], clave_maestra)
        password = descifrar_dato(entry["clave"], clave_maestra)
    except Exception:
        return (None, None)

    return (usuario, password)
