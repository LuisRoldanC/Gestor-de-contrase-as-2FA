# user_utils.py

import os
import json
import pyotp

USERS_FILE = "users.json"

def cargar_usuarios() -> dict:
    """
    Devuelve el contenido de users.json como dict.
    Si no existe, devuelve {}.
    """
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    else:
        return {}

def guardar_usuarios(usuarios: dict) -> None:
    """
    Guarda el dict usuarios en users.json (sobrescribe).
    """
    with open(USERS_FILE, "w") as f:
        json.dump(usuarios, f)

def registrar_usuario(username: str, master_pass: str) -> str:
    """
    Registra un nuevo usuario con:
      - contraseña maestra master_pass (en texto claro, a modo de ejemplo)
      - clave 2FA generada aleatoria
    Devuelve la clave 2FA para que el usuario la agregue en Google Authenticator.
    Si el usuario ya existe, retorna None.
    """
    usuarios = cargar_usuarios()
    username_lower = username.lower()

    if username_lower in usuarios:
        return None  # Ya existe

    # Generar clave 2FA
    secret_2fa = pyotp.random_base32()
    usuarios[username_lower] = {
        "master_pass": master_pass,
        "2fa_secret": secret_2fa
    }
    guardar_usuarios(usuarios)
    return secret_2fa

def validar_usuario(username: str, master_pass: str) -> bool:
    """
    Verifica que username exista y la contraseña maestra coincida.
    """
    usuarios = cargar_usuarios()
    u = usuarios.get(username.lower())
    if not u:
        return False
    return u["master_pass"] == master_pass

def obtener_secret_2fa(username: str) -> str:
    """
    Retorna la clave base32 (2FA) del usuario dado.
    """
    usuarios = cargar_usuarios()
    u = usuarios.get(username.lower())
    if not u:
        return None
    return u["2fa_secret"]
