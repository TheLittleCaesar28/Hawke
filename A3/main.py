# HAWKE - Interfaz Gráfica Básica (Avance 3)
# Los botones aún no ejecutan código

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Colores de la UI
COLOR_BG       = "#1e1e2e"
COLOR_PANEL    = "#2a2a3e"
COLOR_BORDE    = "#44475a"
COLOR_TEXTO    = "#f8f8f2"
COLOR_ACENTO   = "#bd93f9"
COLOR_OK       = "#50fa7b"
COLOR_ERROR    = "#ff5555"
COLOR_WARN     = "#ffb86c"
COLOR_NUM      = "#f1fa8c"
COLOR_KW       = "#8be9fd"


class AppHAWKE:
    def __init__(self, root):
        self.root = root
        self.root.title("HAWKE - Control de Brazo Robótico (Avance 3)")
        self.root.geometry("900x650")
        self.root.configure(bg=COLOR_BG)

        self._construir_menu()
        self._construir_ui()
        self._cargar_ejemplo()

    # ── Menú 

    def _construir_menu(self):
        menu_bar = tk.Menu(self.root, bg=COLOR_PANEL, fg=COLOR_TEXTO)

        archivo = tk.Menu(menu_bar, tearoff=0, bg=COLOR_PANEL, fg=COLOR_TEXTO)
        archivo.add_command(label="Abrir", command=self._abrir_archivo)
        archivo.add_command(label="Guardar", command=self._guardar_archivo)
        archivo.add_separator()
        archivo.add_command(label="Salir", command=self.root.quit)
        menu_bar.add_cascade(label="Archivo", menu=archivo)

        ejecutar = tk.Menu(menu_bar, tearoff=0, bg=COLOR_PANEL, fg=COLOR_TEXTO)
        ejecutar.add_command(label="Ejecutar (F5)", command=self._ejecutar_codigo)
        ejecutar.add_command(label="Limpiar", command=self._limpiar_todo)
        menu_bar.add_cascade(label="Ejecutar", menu=ejecutar)

        self.root.config(menu=menu_bar)
        self.root.bind('<F5>', lambda e: self._ejecutar_codigo())

    # ── Interfaz principal 

    def _construir_ui(self):
        # Frame superior: editor de código
        frame_code = tk.LabelFrame(self.root, text=" CÓDIGO HAWKE ",
                                    bg=COLOR_PANEL, fg=COLOR_ACENTO,
                                    font=("Arial", 10, "bold"))
        frame_code.pack(fill="both", expand=True, padx=10, pady=10)

        self.text_code = tk.Text(
            frame_code,
            font=("Courier New", 11),
            bg="#12121e", fg=COLOR_TEXTO,
            insertbackground=COLOR_TEXTO,
            relief="flat", padx=8, pady=8
        )
        self.text_code.pack(fill="both", expand=True, padx=5, pady=5)

        # Botones
        frame_botones = tk.Frame(self.root, bg=COLOR_BG)
        frame_botones.pack(fill="x", padx=10, pady=5)

        btn_ejecutar = tk.Button(frame_botones, text="▶ Ejecutar (F5)",
                                 command=self._ejecutar_codigo,
                                 bg=COLOR_ACENTO, fg="#282a36",
                                 font=("Arial", 10, "bold"), relief="flat", padx=15)
        btn_ejecutar.pack(side="left", padx=5)

        btn_limpiar = tk.Button(frame_botones, text="🗑 Limpiar",
                                command=self._limpiar_todo,
                                bg=COLOR_PANEL, fg=COLOR_WARN,
                                font=("Arial", 10), relief="flat", padx=15)
        btn_limpiar.pack(side="left", padx=5)

        # Panel de errores
        frame_errors = tk.LabelFrame(self.root, text=" PANEL DE ERRORES ",
                                     bg=COLOR_PANEL, fg=COLOR_ERROR,
                                     font=("Arial", 10, "bold"))
        frame_errors.pack(fill="x", padx=10, pady=5)

        self.text_errors = tk.Text(frame_errors, height=5,
                                   font=("Courier New", 9),
                                   bg="#12121e", fg=COLOR_ERROR,
                                   relief="flat", padx=5, pady=5)
        self.text_errors.pack(fill="both", expand=True, padx=5, pady=5)
        self.text_errors.insert("1.0", "--- Panel de errores ---\n")
        self.text_errors.insert("end", "Los errores se mostrarán aquí\n")
        self.text_errors.insert("end", "(Avance 3: interfaz visual únicamente)\n")

        # Consola de salida
        frame_console = tk.LabelFrame(self.root, text=" CONSOLA DE SALIDA ",
                                      bg=COLOR_PANEL, fg=COLOR_ACENTO,
                                      font=("Arial", 10, "bold"))
        frame_console.pack(fill="both", expand=True, padx=10, pady=5)

        self.text_console = tk.Text(frame_console, height=6,
                                    font=("Courier New", 9),
                                    bg="#12121e", fg=COLOR_OK,
                                    relief="flat", padx=5, pady=5)
        self.text_console.pack(fill="both", expand=True, padx=5, pady=5)
        self.text_console.insert("1.0", "--- Consola de salida ---\n")
        self.text_console.insert("end", "La salida de ejecución se mostrará aquí\n")
        self.text_console.insert("end", "(Avance 3: interfaz visual únicamente)\n")

    # ── Cargar código de ejemplo 

    def _cargar_ejemplo(self):
        codigo = '''GUARDAR AGARRAR {
    MOVER 30 LENTO;
    CERRAR;
    ESPERAR 500;
    MOVER 90 RAPIDO;
};

EJECUTAR AGARRAR;
GIRAR DERECHA 45;
ESPERAR 1000;
ABRIR;
'''
        self.text_code.insert("1.0", codigo)

    # ── Acciones de los botones (Avance 3: solo mensajes) 

    def _ejecutar_codigo(self):
        """Avance 3: Solo muestra un mensaje. En Avance 4 se conectará con lexer/parser."""
        print("[AVANCE 3] Botón Ejecutar presionado")
        print("  (En Avance 4 se implementará la conexión con lexer/parser)")
        
        # Limpiar paneles
        self.text_errors.delete("1.0", tk.END)
        self.text_console.delete("1.0", tk.END)
        
        # Mostrar mensaje de avance
        self.text_console.insert("1.0", "=== AVANCE 3: INTERFAZ GRÁFICA BÁSICA ===\n")
        self.text_console.insert("end", "Botón Ejecutar: conectará con lexer/parser en Avance 4\n")
        self.text_console.insert("end", "Código a analizar:\n")
        self.text_console.insert("end", "-" * 40 + "\n")
        codigo = self.text_code.get("1.0", "end-1c")[:200]
        self.text_console.insert("end", codigo + "\n")
        self.text_console.insert("end", "-" * 40 + "\n")
        self.text_console.insert("end", "\n✅ Avance 3 completado.\n")
        self.text_console.insert("end", "   Próximo: Avance 4 - Conectar lexer/parser\n")

    def _abrir_archivo(self):
        ruta = filedialog.askopenfilename(
            filetypes=[("Archivos HAWKE", "*.hawke"), ("Texto", "*.txt")]
        )
        if ruta:
            with open(ruta, "r", encoding="utf-8") as f:
                contenido = f.read()
            self.text_code.delete("1.0", tk.END)
            self.text_code.insert("1.0", contenido)

    def _guardar_archivo(self):
        ruta = filedialog.asksaveasfilename(
            defaultextension=".hawke",
            filetypes=[("Archivos HAWKE", "*.hawke"), ("Texto", "*.txt")]
        )
        if ruta:
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(self.text_code.get("1.0", "end-1c"))

    def _limpiar_todo(self):
        self.text_code.delete("1.0", tk.END)
        self.text_errors.delete("1.0", tk.END)
        self.text_console.delete("1.0", tk.END)
        self.text_errors.insert("1.0", "--- Panel de errores ---\n")
        self.text_console.insert("1.0", "--- Consola de salida ---\n")


# ── Punto de entrada 

if __name__ == "__main__":
    root = tk.Tk()
    app = AppHAWKE(root)
    root.mainloop()