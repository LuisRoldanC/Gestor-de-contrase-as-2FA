import tkinter as tk
from tkinter import messagebox
import os
import pyotp
import json

from crypto_utils import generar_clave
from storage import guardar_credencial, leer_credencial
from user_utils import registrar_usuario, validar_usuario, obtener_secret_2fa

# Contraseña maestra NO se almacena aquí: cada usuario la define en users.json
# Este valor solo sirve para el usuario “root” por si quieres un admin. En este ejemplo no lo usamos.
# MASTER_PASS = "TuContraseña123"

class PasswordManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Manager Multiusuario")
        self.root.geometry("400x300")
        self.current_user = None  # nombre de usuario en minúsculas

        # Si no existe la clave AES, la generamos
        if not os.path.exists("secret.key"):
            generar_clave()

        # Pantalla inicial: login o registro
        self.build_home_ui()

    # --------------------------------------------
    # PANTALLA INICIAL: Elegir “Registrar” o “Iniciar sesión”
    # --------------------------------------------
    def build_home_ui(self):
        self.clear_ui()
        tk.Label(self.root, text="🔑 Bienvenido", font=("Arial", 16, "bold")).pack(pady=20)

        tk.Button(self.root, text="Registrarse", command=self.build_register_ui, width=20).pack(pady=10)
        tk.Button(self.root, text="Iniciar sesión", command=self.build_login_ui, width=20).pack(pady=10)

    # --------------------------------------------
    # REGISTRO DE UN NUEVO USUARIO
    # --------------------------------------------
    def build_register_ui(self):
        self.clear_ui()
        tk.Label(self.root, text="🆕 Registrarse", font=("Arial", 14, "bold")).pack(pady=10)

        tk.Label(self.root, text="Usuario:").pack()
        self.entry_reg_user = tk.Entry(self.root)
        self.entry_reg_user.pack(pady=5)

        tk.Label(self.root, text="Contraseña maestra:").pack()
        self.entry_reg_pass1 = tk.Entry(self.root, show="*")
        self.entry_reg_pass1.pack(pady=5)

        tk.Label(self.root, text="Confirmar contraseña:").pack()
        self.entry_reg_pass2 = tk.Entry(self.root, show="*")
        self.entry_reg_pass2.pack(pady=5)

        tk.Button(self.root, text="Registrar", command=self.register_user, width=20).pack(pady=15)
        tk.Button(self.root, text="Volver", command=self.build_home_ui, width=20).pack()

    def register_user(self):
        username = self.entry_reg_user.get().strip()
        pass1 = self.entry_reg_pass1.get()
        pass2 = self.entry_reg_pass2.get()

        if not username or not pass1:
            messagebox.showerror("Error", "Usuario y contraseña no pueden estar vacíos.")
            return
        if pass1 != pass2:
            messagebox.showerror("Error", "Las contraseñas no coinciden.")
            return

        # Llamamos a user_utils.registrar_usuario
        secret_2fa = registrar_usuario(username, pass1)
        if secret_2fa is None:
            messagebox.showerror("Error", "El usuario ya existe. Intenta otro nombre.")
            return

        # Mostramos la clave 2FA para que el usuario la agregue en Google Authenticator
        msg = (
            f"Usuario registrado correctamente.\n\n"
            f"Clave para 2FA (copiar en Google Authenticator):\n\n"
            f"{secret_2fa}\n\n"
            "Abre la app y escanea o ingresa esta clave.\n\n"
            "Luego presiona Aceptar para volver al inicio."
        )
        messagebox.showinfo("Registro exitoso", msg)
        self.build_home_ui()

    # --------------------------------------------
    # LOGIN: Nombre de usuario + Contraseña maestra
    # --------------------------------------------
    def build_login_ui(self):
        self.clear_ui()
        tk.Label(self.root, text="🔐 Iniciar sesión", font=("Arial", 14, "bold")).pack(pady=10)

        tk.Label(self.root, text="Usuario:").pack()
        self.entry_login_user = tk.Entry(self.root)
        self.entry_login_user.pack(pady=5)

        tk.Label(self.root, text="Contraseña maestra:").pack()
        self.entry_login_pass = tk.Entry(self.root, show="*")
        self.entry_login_pass.pack(pady=5)

        tk.Button(self.root, text="Continuar", command=self.verify_login, width=20).pack(pady=15)
        tk.Button(self.root, text="Volver", command=self.build_home_ui, width=20).pack()

    def verify_login(self):
        username = self.entry_login_user.get().strip()
        master_pass = self.entry_login_pass.get()

        if not validar_usuario(username, master_pass):
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")
            return

        # Ahora, si la contraseña maestra coincide, abrimos ventana 2FA
        self.current_user = username.lower()
        self.mostrar_ventana_2fa()

    # --------------------------------------------
    # VENTANA 2FA: Ingresar código generado por Google Authenticator
    # --------------------------------------------
    def mostrar_ventana_2fa(self):
        ventana_2fa = tk.Toplevel(self.root)
        ventana_2fa.title("Código 2FA")
        ventana_2fa.geometry("300x150")

        tk.Label(ventana_2fa, text="Introduce el código 2FA:", font=("Arial", 12)).pack(pady=10)
        entry_2fa = tk.Entry(ventana_2fa)
        entry_2fa.pack(pady=5)

        def verificar_codigo():
            codigo = entry_2fa.get().strip()
            secret = obtener_secret_2fa(self.current_user)
            totp = pyotp.TOTP(secret)
            if totp.verify(codigo):
                ventana_2fa.destroy()
                self.build_main_ui()
            else:
                messagebox.showerror("Error", "Código 2FA inválido.")

        tk.Button(ventana_2fa, text="Verificar", command=verificar_codigo, width=15).pack(pady=10)

    # --------------------------------------------
    # INTERFAZ PRINCIPAL (YA LOGUEADO)
    # --------------------------------------------
    def build_main_ui(self):
        self.clear_ui()
        tk.Label(self.root, text=f"👤 Usuario: {self.current_user}", font=("Arial", 12)).pack(pady=5)
        tk.Label(self.root, text="🔒 Gestor de Contraseñas", font=("Arial", 14, "bold")).pack(pady=10)

        tk.Button(self.root, text="Guardar credencial", command=self.guardar, width=25).pack(pady=5)
        tk.Button(self.root, text="Leer credencial", command=self.leer, width=25).pack(pady=5)
        tk.Button(self.root, text="Cerrar sesión", command=self.cerrar_sesion, width=25).pack(pady=5)
        tk.Button(self.root, text="Salir", command=self.root.destroy, width=25).pack(pady=5)

    def cerrar_sesion(self):
        self.current_user = None
        self.build_home_ui()

    # --------------------------------------------
    # GUARDAR CREDENCIAL (usa storage.guardar_credencial)
    # --------------------------------------------
    def guardar(self):
        win = tk.Toplevel(self.root)
        win.title("Guardar credencial")
        win.geometry("320x220")

        tk.Label(win, text="Servicio:").pack(pady=(10, 0))
        entry_servicio = tk.Entry(win)
        entry_servicio.pack(pady=5)

        tk.Label(win, text="Usuario:").pack(pady=(10, 0))
        entry_usuario = tk.Entry(win)
        entry_usuario.pack(pady=5)

        tk.Label(win, text="Contraseña:").pack(pady=(10, 0))
        entry_clave = tk.Entry(win)
        entry_clave.pack(pady=5)

        def guardar_datos():
            servicio = entry_servicio.get().strip()
            usuario = entry_usuario.get().strip()
            clave = entry_clave.get().strip()
            if not servicio or not usuario or not clave:
                messagebox.showerror("Error", "Todos los campos son obligatorios.")
                return

            guardar_credencial(self.current_user, servicio, usuario, clave)
            messagebox.showinfo("Éxito", f"Credencial para '{servicio}' guardada.")
            win.destroy()

        tk.Button(win, text="Guardar", command=guardar_datos, width=20).pack(pady=15)

    # --------------------------------------------
    # LEER CREDENCIAL (usa storage.leer_credencial)
    # --------------------------------------------
    def leer(self):
        win = tk.Toplevel(self.root)
        win.title("Leer credencial")
        win.geometry("300x150")

        tk.Label(win, text="Servicio:").pack(pady=(10, 0))
        entry_servicio = tk.Entry(win)
        entry_servicio.pack(pady=5)

        def buscar():
            servicio = entry_servicio.get().strip()
            if not servicio:
                messagebox.showerror("Error", "Ingresa un servicio.")
                return

            usuario, password = leer_credencial(self.current_user, servicio)
            if usuario is None:
                messagebox.showerror("Error", f"No se encontró credencial para '{servicio}'.")
                return

            # Si existe, abrimos otra ventana con los resultados
            resultado = tk.Toplevel(self.root)
            resultado.title(f"Credencial de {servicio}")
            resultado.geometry("350x180")

            tk.Label(resultado, text=f"Servicio: {servicio}", font=("Arial", 12, "bold")).pack(pady=5)
            tk.Label(resultado, text=f"Usuario: {usuario}", font=("Arial", 11)).pack(pady=5)
            tk.Label(resultado, text=f"Contraseña: {password}", font=("Arial", 11)).pack(pady=5)

            tk.Button(resultado, text="Cerrar", command=resultado.destroy, width=15).pack(pady=10)
            win.destroy()

        tk.Button(win, text="Buscar", command=buscar, width=15).pack(pady=15)

    # --------------------------------------------
    # Util: limpiar todo el contenido de la ventana
    # --------------------------------------------
    def clear_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManagerApp(root)
    root.mainloop()
