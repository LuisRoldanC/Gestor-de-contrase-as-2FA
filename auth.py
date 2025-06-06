import pyotp
import json

def configurar_2fa():
    secret = pyotp.random_base32()
    print("🔐 Clave 2FA (añádela a Google Authenticator):", secret)
    with open("config.json", "w") as f:
        json.dump({"2fa_secret": secret}, f)

def verificar_2fa():
    with open("config.json") as f:
        config = json.load(f)
    secret = config["2fa_secret"]
    totp = pyotp.TOTP(secret)
    codigo = input("Introduce el código 2FA: ")
    return totp.verify(codigo)
