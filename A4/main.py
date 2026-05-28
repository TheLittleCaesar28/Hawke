# HAWKE - Interfaz Gráfica Funcional (Avance 4)
# Conexión completa con lexer, parser y ejecución

import tkinter as tk
from tkinter import ttk, filedialog
import math

from lexer import Lexer
from parser import Parser
from tabla_simbolos import TablaSimbolos


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
        self.root.title("HAWKE - Control de Brazo Robótico")
        self.root.geometry("1100x750")
        self.root.configure(bg=COLOR_BG)

        self.estado = {
            'pinza': 0,
            'brazo_h': 90,
            'brazo_v': 45,
        }

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
        # Frame superior: visualización + código
        top_frame = tk.Frame(self.root, bg=COLOR_BG)
        top_frame.pack(fill="both", expand=True, padx=8, pady=(8, 4))

        self._panel_visualizacion(top_frame)
        self._panel_codigo(top_frame)

        # Frame inferior: errores + estado + consola
        bot_frame = tk.Frame(self.root, bg=COLOR_BG)
        bot_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self._panel_errores(bot_frame)
        self._panel_estado(bot_frame)
        self._panel_consola(bot_frame)

    # ── Panel de visualización del brazo 

    def _panel_visualizacion(self, parent):
        frame = tk.LabelFrame(parent, text=" VISUALIZACION DEL BRAZO ",
                              bg=COLOR_PANEL, fg=COLOR_ACENTO,
                              font=("Arial", 9, "bold"))
        frame.pack(side="left", fill="both", expand=True, padx=(0, 4))

        self.canvas = tk.Canvas(frame, bg="#12121e", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=4, pady=4)
        self.canvas.bind("<Configure>", lambda e: self._dibujar_brazo())

    def _dibujar_brazo(self):
        c = self.canvas
        c.delete("all")

        w = c.winfo_width()
        h = c.winfo_height()
        if w < 10 or h < 10:
            return

        cx = w // 2
        cy = h - 40

        # Base
        c.create_oval(cx-20, cy-10, cx+20, cy+10, fill="#6272a4", outline=COLOR_BORDE)
        c.create_text(cx, cy, text="BASE", fill=COLOR_TEXTO, font=("Arial", 7))

        # Brazo vertical
        ang_v = math.radians(180 - self.estado['brazo_v'])
        largo = min(w, h) * 0.35
        bx = cx + largo * math.cos(ang_v)
        by = cy + largo * math.sin(ang_v)
        c.create_line(cx, cy, bx, by, width=8, fill="#6272a4", capstyle="round")

        # Brazo horizontal
        ang_h = math.radians(180 - self.estado['brazo_h'])
        largo2 = largo * 0.65
        ex = bx + largo2 * math.cos(ang_h)
        ey = by + largo2 * math.sin(ang_h)
        c.create_line(bx, by, ex, ey, width=6, fill="#bd93f9", capstyle="round")

        # Pinzas
        apertura = (self.estado['pinza'] / 180) * 18
        c.create_line(ex, ey, ex - 12, ey - 18 + apertura,
                      width=4, fill=COLOR_OK, capstyle="round")
        c.create_line(ex, ey, ex + 12, ey - 18 + apertura,
                      width=4, fill=COLOR_OK, capstyle="round")

        # Etiquetas de estado
        c.create_text(10, 12, anchor="w", fill=COLOR_NUM, font=("Courier", 9),
                      text=f"Pinza: {self.estado['pinza']}°")
        c.create_text(10, 26, anchor="w", fill=COLOR_NUM, font=("Courier", 9),
                      text=f"H: {self.estado['brazo_h']}°   V: {self.estado['brazo_v']}°")

    # ── Panel de código 

    def _panel_codigo(self, parent):
        frame = tk.LabelFrame(parent, text=" CODIGO HAWKE ",
                              bg=COLOR_PANEL, fg=COLOR_ACENTO,
                              font=("Arial", 9, "bold"))
        frame.pack(side="right", fill="both", expand=True, padx=(4, 0))

        self.text_code = tk.Text(frame, font=("Courier New", 11),
                                 bg="#12121e", fg=COLOR_TEXTO,
                                 insertbackground=COLOR_TEXTO,
                                 relief="flat", padx=8, pady=8)
        self.text_code.pack(fill="both", expand=True, padx=4, pady=4)

        # Botones
        btn_frame = tk.Frame(frame, bg=COLOR_PANEL)
        btn_frame.pack(fill="x", padx=4, pady=(0, 4))

        tk.Button(btn_frame, text="▶ Ejecutar (F5)", command=self._ejecutar_codigo,
                  bg=COLOR_ACENTO, fg="#282a36", font=("Arial", 9, "bold"),
                  relief="flat", padx=10).pack(side="left", padx=(0, 4))

        tk.Button(btn_frame, text="📂 Abrir", command=self._abrir_archivo,
                  bg=COLOR_PANEL, fg=COLOR_TEXTO, font=("Arial", 9),
                  relief="flat", padx=8).pack(side="left", padx=2)

        tk.Button(btn_frame, text="💾 Guardar", command=self._guardar_archivo,
                  bg=COLOR_PANEL, fg=COLOR_TEXTO, font=("Arial", 9),
                  relief="flat", padx=8).pack(side="left", padx=2)

        tk.Button(btn_frame, text="🗑 Limpiar", command=self._limpiar_todo,
                  bg=COLOR_PANEL, fg=COLOR_WARN, font=("Arial", 9),
                  relief="flat", padx=8).pack(side="right", padx=2)

    # ── Panel de errores 

    def _panel_errores(self, parent):
        frame = tk.LabelFrame(parent, text=" PANEL DE ERRORES ",
                              bg=COLOR_PANEL, fg=COLOR_ERROR,
                              font=("Arial", 9, "bold"))
        frame.pack(side="left", fill="both", expand=True, padx=(0, 4))

        self.text_errors = tk.Text(frame, height=8, font=("Courier New", 9),
                                   bg="#12121e", fg=COLOR_ERROR,
                                   relief="flat", padx=6, pady=6)
        self.text_errors.pack(fill="both", expand=True, padx=4, pady=4)

    # ── Panel de estado del brazo 

    def _panel_estado(self, parent):
        frame = tk.LabelFrame(parent, text=" ESTADO DEL BRAZO ",
                              bg=COLOR_PANEL, fg=COLOR_OK,
                              font=("Arial", 9, "bold"))
        frame.pack(side="left", fill="y", padx=4)

        self.lbl_pinza = tk.Label(frame, text="Pinza: 0° (ABIERTA)",
                                  bg=COLOR_PANEL, fg=COLOR_NUM,
                                  font=("Courier New", 10), anchor="w")
        self.lbl_pinza.pack(anchor="w", padx=12, pady=(10, 2))

        self.lbl_h = tk.Label(frame, text="Horiz: 90°", bg=COLOR_PANEL,
                              fg=COLOR_NUM, font=("Courier New", 10), anchor="w")
        self.lbl_h.pack(anchor="w", padx=12, pady=2)

        self.lbl_v = tk.Label(frame, text="Vert: 45°", bg=COLOR_PANEL,
                              fg=COLOR_NUM, font=("Courier New", 10), anchor="w")
        self.lbl_v.pack(anchor="w", padx=12, pady=2)

        self.lbl_vel = tk.Label(frame, text="Vel: NORMAL", bg=COLOR_PANEL,
                                fg=COLOR_NUM, font=("Courier New", 10), anchor="w")
        self.lbl_vel.pack(anchor="w", padx=12, pady=(2, 10))

    # ── Panel de consola 

    def _panel_consola(self, parent):
        frame = tk.LabelFrame(parent, text=" CONSOLA DE SALIDA ",
                              bg=COLOR_PANEL, fg=COLOR_ACENTO,
                              font=("Arial", 9, "bold"))
        frame.pack(side="right", fill="both", expand=True, padx=(4, 0))

        self.text_console = tk.Text(frame, height=8, font=("Courier New", 9),
                                    bg="#12121e", fg=COLOR_OK,
                                    relief="flat", padx=6, pady=6)
        self.text_console.pack(fill="both", expand=True, padx=4, pady=4)

    # ── Lógica de ejecución 

    def _ejecutar_codigo(self):
        codigo = self.text_code.get("1.0", "end-1c")

        self.text_errors.delete("1.0", "end")
        self.text_console.delete("1.0", "end")

        # FASE 1: LEXER
        self._log("="*60 + "\n")
        self._log("HAWKE v2.0 - EJECUCIÓN\n")
        self._log("="*60 + "\n\n")

        self._log("🔍 FASE 1: ANÁLISIS LÉXICO\n")
        lexer = Lexer(codigo)
        tokens, pila_lex = lexer.obtener_tokens()

        self._log(f"  → {len(tokens)} tokens encontrados\n")

        if pila_lex.hay_errores():
            self._mostrar_errores(pila_lex, "LÉXICOS")
            return

        # Mostrar tokens (opcional)
        for tok in tokens[:10]:
            self._log(f"     {tok[0]}: '{tok[1]}'\n")
        if len(tokens) > 10:
            self._log(f"     ... y {len(tokens)-10} más\n")

        # FASE 2: PARSER
        self._log("\n🔍 FASE 2: ANÁLISIS SINTÁCTICO\n")
        parser = Parser(tokens)
        instrucciones, pila_par = parser.parse()

        if pila_par.hay_errores():
            self._mostrar_errores(pila_par, "SINTÁCTICOS/SEMÁNTICOS")
            return

        self._log(f"  → {len(instrucciones)} instrucciones reconocidas\n")

        # FASE 3: EJECUCIÓN
        self._log("\n🚀 FASE 3: EJECUCIÓN\n")
        self._simular(instrucciones, parser.tabla_sim)

        self._log("\n✅ PROGRAMA FINALIZADO SIN ERRORES\n", COLOR_OK)

    def _simular(self, instrucciones, tabla_sim, indent=0):
        pre = "  " * indent
        for inst in instrucciones:
            cmd = inst[0]

            if cmd == 'ABRIR':
                self.estado['pinza'] = 0
                self._log(f"{pre}→ ABRIR pinzas\n")

            elif cmd == 'CERRAR':
                self.estado['pinza'] = 180
                self._log(f"{pre}→ CERRAR pinzas\n")

            elif cmd == 'MOVER':
                _, angulo, vel = inst
                self.estado['brazo_v'] = angulo
                self._log(f"{pre}→ MOVER brazo a {angulo}° [{vel}]\n")

            elif cmd == 'GIRAR':
                _, direccion, angulo, vel = inst
                self.estado['brazo_h'] = angulo
                self._log(f"{pre}→ GIRAR {direccion} {angulo}° [{vel}]\n")

            elif cmd == 'ESPERAR':
                _, ms = inst
                self._log(f"{pre}→ ESPERAR {ms} ms\n")

            elif cmd == 'GUARDAR':
                _, nombre, _ = inst
                self._log(f"{pre}→ GUARDAR rutina '{nombre}'\n")

            elif cmd == 'EJECUTAR':
                _, nombre = inst
                rutina = tabla_sim.obtener_rutina(nombre)
                if rutina:
                    self._log(f"{pre}→ EJECUTAR '{nombre}':\n")
                    self._simular(rutina, tabla_sim, indent + 1)

            elif cmd == 'REPETIR':
                _, n, bloque = inst
                self._log(f"{pre}→ REPETIR {n} veces:\n")
                for _ in range(n):
                    self._simular(bloque, tabla_sim, indent + 1)

        self._actualizar_estado_ui()

    def _actualizar_estado_ui(self):
        p = self.estado['pinza']
        txt_p = "ABIERTA" if p == 0 else ("CERRADA" if p == 180 else f"PARCIAL")
        self.lbl_pinza.config(text=f"Pinza: {p}° ({txt_p})")
        self.lbl_h.config(text=f"Horiz: {self.estado['brazo_h']}°")
        self.lbl_v.config(text=f"Vert: {self.estado['brazo_v']}°")
        self._dibujar_brazo()

    def _mostrar_errores(self, pila, titulo):
        self.text_errors.insert("end", f"--- Errores {titulo} ---\n\n")
        for e in pila.pila:
            self.text_errors.insert("end", f"[{e.tipo}] L{e.linea}:C{e.columna} '{e.token}'\n")
            self.text_errors.insert("end", f"  Problema: {e.descripcion}\n")
            self.text_errors.insert("end", f"  Solución: {e.solucion}\n\n")

    def _log(self, texto, color=None):
        self.text_console.insert("end", texto)
        self.text_console.see("end")
        print(texto, end="")

    # ── Archivo 

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

    def _abrir_archivo(self):
        ruta = filedialog.askopenfilename(
            filetypes=[("Archivos HAWKE", "*.hawke"), ("Texto", "*.txt")]
        )
        if ruta:
            with open(ruta, "r", encoding="utf-8") as f:
                contenido = f.read()
            self.text_code.delete("1.0", "end")
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
        self.text_code.delete("1.0", "end")
        self.text_errors.delete("1.0", "end")
        self.text_console.delete("1.0", "end")
        self.estado = {'pinza': 0, 'brazo_h': 90, 'brazo_v': 45}
        self._actualizar_estado_ui()


# ── Punto de entrada 

if __name__ == "__main__":
    root = tk.Tk()
    app = AppHAWKE(root)
    root.mainloop()