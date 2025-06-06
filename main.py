from getpass import getpass
from auth import verificar_2fa
from storage import guardar_credencial, leer_credencial
from crypto_utils import generar_clave
import os
from getpass import getpass


def main():
    print("🔐 Password Manager")

    if not os.path.exists("secret.key"):
        print("[*] Generando clave AES...")
        generar_clave()

    master = input("Contraseña maestra: ")
    if master != "TuContraseña123":
        print("❌ Contraseña incorrecta.")
        return

    if not verificar_2fa():
        print("❌ Código 2FA inválido.")
        return

    print("\n1. Guardar nueva credencial\n2. Leer credencial")
    opcion = input("Opción: ")

    if opcion == "1":
        servicio = input("Servicio: ")
        usuario = input("Usuario: ")
        clave = input("Contraseña: ")
        guardar_credencial(servicio, usuario, clave)
    elif opcion == "2":
        servicio = input("Servicio a consultar: ")
        leer_credencial(servicio)
    else:
        print("Opción inválida.")

if __name__ == "__main__":
    main()
