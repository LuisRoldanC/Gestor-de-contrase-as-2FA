from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64

def generar_clave():
    clave = get_random_bytes(32)
    with open("secret.key", "wb") as f:
        f.write(clave)

def cargar_clave():
    with open("secret.key", "rb") as f:
        return f.read()

def cifrar_dato(dato, clave):
    cipher = AES.new(clave, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(dato.encode('utf-8'))
    return base64.b64encode(nonce + tag + ciphertext).decode('utf-8')

def descifrar_dato(data_cifrada, clave):
    raw = base64.b64decode(data_cifrada)
    nonce = raw[:16]
    tag = raw[16:32]
    ciphertext = raw[32:]
    cipher = AES.new(clave, AES.MODE_EAX, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')
