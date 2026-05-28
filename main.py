import tkinter as tk
from tkinter import filedialog, messagebox
import math
import time
import threading

from lexer import Lexer
from parser import Parser
from tabla_simbolos import TablaSimbolos
from pila_errores import Error, PilaErrores
from brazo_esp32 import BrazoESP32


# ── Paleta de colores ──────────────────────────────────────────────────────────
COLOR_BG      = "#0f0f1a"
COLOR_PANEL   = "#1a1a2e"
COLOR_PANEL2  = "#16213e"
COLOR_BORDE   = "#2d2d4e"
COLOR_BORDE2  = "#3d3d6e"
COLOR_TEXTO   = "#e8e8f0"
COLOR_TEXTO2  = "#a0a0c0"
COLOR_ACENTO  = "#bd93f9"
COLOR_ACENTO2 = "#8a63d2"
COLOR_OK      = "#50fa7b"
COLOR_ERROR   = "#ff5555"
COLOR_WARN    = "#ffb86c"
COLOR_NUM     = "#f1fa8c"
COLOR_KW      = "#8be9fd"
COLOR_CANVAS  = "#080810"

ARM_SEG1      = "#8be9fd"
ARM_SEG1_DARK = "#3a6080"
ARM_SEG2      = "#50fa7b"
ARM_SEG2_DARK = "#1a5a2a"
ARM_JOINT1    = "#ffb86c"
ARM_JOINT2    = "#ff5555"
ARM_GRIPPER   = "#f1fa8c"
ARM_BASE_L    = "#6272a4"
ARM_BASE_D    = "#44475a"


class AppHAWKE:
    def __init__(self, root):
        self.root = root
        self.root.title("HAWKE — Control de Brazo Robótico")
        self.root.geometry("1200x780")
        self.root.configure(bg=COLOR_BG)
        self.root.minsize(900, 600)

        self.estado = {
            'pinza': 0,
            'brazo_h': 90,
            'brazo_v': 45,
            'velocidad': 'NORMAL'
        }

        self.brazo      = None
        self.modo_fisico = False
        self.ejecutando  = False

        # Animación suave
        self._anim_h  = 90.0
        self._anim_v  = 45.0
        self._anim_p  = 0.0
        self._anim_on = True

        self._construir_menu()
        self._construir_ui()
        self._cargar_ejemplo()
        self._iniciar_animacion()

    # ── Menú ───────────────────────────────────────────────────────────────────

    def _construir_menu(self):
        mb = tk.Menu(self.root, bg=COLOR_PANEL, fg=COLOR_TEXTO,
                     activebackground=COLOR_ACENTO2, activeforeground=COLOR_TEXTO,
                     relief="flat", bd=0)

        arch = tk.Menu(mb, tearoff=0, bg=COLOR_PANEL, fg=COLOR_TEXTO,
                       activebackground=COLOR_ACENTO2, activeforeground=COLOR_TEXTO)
        arch.add_command(label="  Nuevo",     command=self._nuevo_archivo)
        arch.add_command(label="  Abrir",    command=self._abrir_archivo)
        arch.add_command(label="  Guardar",  command=self._guardar_archivo)
        arch.add_command(label="  Guardar como...", command=self._guardar_como)
        arch.add_separator()
        arch.add_command(label="  Salir",    command=self._salir)
        mb.add_cascade(label=" Archivo ", menu=arch)

        ejec = tk.Menu(mb, tearoff=0, bg=COLOR_PANEL, fg=COLOR_TEXTO,
                       activebackground=COLOR_ACENTO2, activeforeground=COLOR_TEXTO)
        ejec.add_command(label="  Ejecutar (F5)", command=self._ejecutar_codigo)
        ejec.add_command(label="  Detener",       command=self._detener_ejecucion)
        ejec.add_command(label="  Limpiar todo",  command=self._limpiar_todo)
        mb.add_cascade(label=" Ejecutar ", menu=ejec)

        ayuda = tk.Menu(mb, tearoff=0, bg=COLOR_PANEL, fg=COLOR_TEXTO,
                        activebackground=COLOR_ACENTO2, activeforeground=COLOR_TEXTO)
        ayuda.add_command(label="  Documentación",  command=self._mostrar_documentacion)
        ayuda.add_command(label="  ABOUT",   command=self._mostrar_about)
        mb.add_cascade(label=" Ayuda ", menu=ayuda)

        self.root.config(menu=mb)
        self.root.bind('<F5>', lambda e: self._ejecutar_codigo())

    # ── Construcción principal ─────────────────────────────────────────────────

    def _construir_ui(self):
        top = tk.Frame(self.root, bg=COLOR_BG)
        top.pack(fill="both", expand=True, padx=10, pady=(10, 5))

        self._panel_visualizacion(top)
        self._panel_codigo(top)

        bot = tk.Frame(self.root, bg=COLOR_BG)
        bot.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self._panel_errores(bot)
        self._panel_estado(bot)
        self._panel_consola(bot)

    # ── Helper: panel con borde de acento ──────────────────────────────────────

    def _make_panel(self, title, accent):
        wrapper = tk.Frame(self.root, bg=accent, padx=1, pady=1)
        inner   = tk.Frame(wrapper, bg=COLOR_PANEL)
        inner.pack(fill="both", expand=True)

        hdr = tk.Frame(inner, bg=COLOR_PANEL2)
        hdr.pack(fill="x")
        tk.Label(hdr, text=title, bg=COLOR_PANEL2, fg=accent,
                 font=("Courier New", 9, "bold"),
                 padx=10, pady=6).pack(side="left")
        tk.Frame(inner, bg=COLOR_BORDE, height=1).pack(fill="x")

        return wrapper, inner

    def _btn(self, parent, text, cmd, bg=None, fg=None, bold=False):
        bg     = bg or COLOR_PANEL
        fg     = fg or COLOR_TEXTO
        weight = "bold" if bold else "normal"
        return tk.Button(parent, text=text, command=cmd,
                         bg=bg, fg=fg,
                         font=("Courier New", 9, weight),
                         relief="flat", padx=8, pady=4,
                         activebackground=COLOR_BORDE2,
                         activeforeground=COLOR_TEXTO,
                         cursor="hand2")

    # ── Panel Visualización ────────────────────────────────────────────────────

    def _panel_visualizacion(self, parent):
        wrap, inner = self._make_panel(" ◉  VISUALIZACIÓN DEL BRAZO ", COLOR_ACENTO)
        wrap.pack(in_=parent, side="left", fill="both", expand=True, padx=(0, 5))

        self.canvas = tk.Canvas(inner, bg=COLOR_CANVAS, highlightthickness=0,
                                cursor="crosshair")
        self.canvas.pack(fill="both", expand=True, padx=6, pady=6)
        self.canvas.bind("<Configure>", lambda e: self._dibujar_brazo())

    # ── Panel Código ───────────────────────────────────────────────────────────

    def _panel_codigo(self, parent):
        wrap, inner = self._make_panel(" ✦  CÓDIGO HAWKE ", COLOR_KW)
        wrap.pack(in_=parent, side="right", fill="both", expand=True, padx=(5, 0))

        ef = tk.Frame(inner, bg=COLOR_CANVAS)
        ef.pack(fill="both", expand=True, padx=6, pady=(6, 0))

        self.line_nums = tk.Text(ef, width=3,
                                 font=("Courier New", 11),
                                 bg="#0c0c18", fg="#44475a",
                                 relief="flat", padx=4, pady=6,
                                 state="disabled", cursor="arrow")
        self.line_nums.pack(side="left", fill="y")

        self.text_code = tk.Text(ef, font=("Courier New", 11),
                                 bg=COLOR_CANVAS, fg=COLOR_TEXTO,
                                 insertbackground=COLOR_ACENTO,
                                 relief="flat", wrap="none",
                                 padx=8, pady=6,
                                 selectbackground=COLOR_ACENTO2,
                                 selectforeground=COLOR_TEXTO,
                                 tabs="28p")

        sy = tk.Scrollbar(ef, orient="vertical",
                          command=self._scroll_sync,
                          bg=COLOR_PANEL, troughcolor=COLOR_BG)
        sx = tk.Scrollbar(inner, orient="horizontal",
                          command=self.text_code.xview,
                          bg=COLOR_PANEL, troughcolor=COLOR_BG)

        self.text_code.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        sy.pack(side="right", fill="y")
        self.text_code.pack(side="left", fill="both", expand=True)
        sx.pack(fill="x", padx=6, pady=(0, 2))

        self.text_code.bind('<KeyRelease>', self._update_line_nums)
        self.text_code.bind('<MouseWheel>', self._on_mousewheel)

        bf = tk.Frame(inner, bg=COLOR_PANEL)
        bf.pack(fill="x", padx=6, pady=(0, 6))

        self._btn(bf, "▶ Ejecutar (F5)", self._ejecutar_codigo,
                  bg=COLOR_ACENTO, fg="#1a1a2e", bold=True).pack(side="left", padx=(0, 4))
        self._btn(bf, "■ Detener",  self._detener_ejecucion,
                  bg=COLOR_WARN,   fg="#1a1a2e").pack(side="left", padx=2)
        self._btn(bf, "📂 Abrir",   self._abrir_archivo).pack(side="left", padx=2)
        self._btn(bf, "💾 Guardar", self._guardar_archivo).pack(side="left", padx=2)
        self._btn(bf, "🗑 Limpiar", self._limpiar_todo, fg=COLOR_WARN).pack(side="left", padx=2)

        self._btn(bf, "📋 Tabla Símb.", self._mostrar_tabla_simbolos,
                  fg=COLOR_ACENTO).pack(side="right", padx=2)
        self._btn(bf, "🔌 Desconectar", self._desconectar_brazo,
                  fg=COLOR_ERROR).pack(side="right", padx=2)
        self._btn(bf, "🔌 Conectar",   self._conectar_brazo,
                  fg=COLOR_OK).pack(side="right", padx=2)

    def _scroll_sync(self, *args):
        self.text_code.yview(*args)
        self.line_nums.yview(*args)

    def _on_mousewheel(self, event):
        self.line_nums.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _update_line_nums(self, event=None):
        self.line_nums.config(state="normal")
        self.line_nums.delete("1.0", "end")
        n = self.text_code.get("1.0", "end").count('\n')
        self.line_nums.insert("1.0", "\n".join(str(i) for i in range(1, n + 2)))
        self.line_nums.config(state="disabled")

    # ── Panel Errores ──────────────────────────────────────────────────────────

    def _panel_errores(self, parent):
        wrap, inner = self._make_panel(" ✖  PANEL DE ERRORES ", COLOR_ERROR)
        wrap.pack(in_=parent, side="left", fill="both", expand=True, padx=(0, 5))

        self.text_errors = tk.Text(inner, font=("Courier New", 9),
                                   bg=COLOR_CANVAS, fg=COLOR_ERROR,
                                   relief="flat", padx=8, pady=8,
                                   state="normal")
        sc = tk.Scrollbar(inner, orient="vertical",
                          command=self.text_errors.yview,
                          bg=COLOR_PANEL, troughcolor=COLOR_BG)
        self.text_errors.configure(yscrollcommand=sc.set)
        sc.pack(side="right", fill="y")
        self.text_errors.pack(fill="both", expand=True, padx=(6, 0), pady=6)
        self.text_errors.insert("end", "✅ Esperando ejecución...\n")

    # ── Panel Estado ───────────────────────────────────────────────────────────

    def _panel_estado(self, parent):
        wrap, inner = self._make_panel(" ● ESTADO ", COLOR_OK)
        wrap.pack(in_=parent, side="left", fill="y", padx=5)

        def row(lbl, default, col=COLOR_NUM):
            f = tk.Frame(inner, bg=COLOR_PANEL2,
                         highlightbackground=COLOR_BORDE, highlightthickness=1)
            f.pack(fill="x", padx=6, pady=2)
            tk.Label(f, text=lbl, bg=COLOR_PANEL2, fg=COLOR_TEXTO2,
                     font=("Courier New", 9), padx=8, pady=5).pack(side="left")
            v = tk.Label(f, text=default, bg=COLOR_PANEL2, fg=col,
                         font=("Courier New", 10, "bold"), padx=8)
            v.pack(side="right")
            return v

        self.lbl_pinza = row("Pinza",   "0° ABIERTA")
        self.lbl_h     = row("Base H",  "90°")
        self.lbl_v     = row("Brazo V", "45°")
        self.lbl_vel   = row("Veloc.",  "NORMAL")

        tk.Frame(inner, bg=COLOR_BORDE, height=1).pack(fill="x", padx=6, pady=6)

        self.lbl_conexion = tk.Label(inner, text="⬤  SIMULACIÓN",
                                     bg=COLOR_PANEL2, fg=COLOR_WARN,
                                     font=("Courier New", 9, "bold"),
                                     pady=6, padx=8,
                                     highlightbackground=COLOR_BORDE,
                                     highlightthickness=1)
        self.lbl_conexion.pack(fill="x", padx=6, pady=(0, 6))

    # ── Panel Consola ──────────────────────────────────────────────────────────

    def _panel_consola(self, parent):
        wrap, inner = self._make_panel(" ▸  CONSOLA DE SALIDA ", COLOR_OK)
        wrap.pack(in_=parent, side="right", fill="both", expand=True, padx=(5, 0))

        self.text_console = tk.Text(inner, font=("Courier New", 9),
                                    bg=COLOR_CANVAS, fg=COLOR_OK,
                                    relief="flat", padx=8, pady=8)
        sc = tk.Scrollbar(inner, orient="vertical",
                          command=self.text_console.yview,
                          bg=COLOR_PANEL, troughcolor=COLOR_BG)
        self.text_console.configure(yscrollcommand=sc.set)
        sc.pack(side="right", fill="y")
        self.text_console.pack(fill="both", expand=True, padx=(6, 0), pady=6)

    # ── Animación suave del brazo ──────────────────────────────────────────────

    def _iniciar_animacion(self):
        def tick():
            changed = False
            for attr, key in [('_anim_h', 'brazo_h'),
                               ('_anim_v', 'brazo_v'),
                               ('_anim_p', 'pinza')]:
                cur = getattr(self, attr)
                tgt = float(self.estado[key])
                d   = tgt - cur
                if abs(d) > 0.3:
                    setattr(self, attr, cur + d * 0.14)
                    changed = True
                else:
                    setattr(self, attr, tgt)
            if changed:
                try:
                    self._dibujar_brazo()
                except Exception:
                    pass
            if self._anim_on:
                self.root.after(16, tick)

        self.root.after(16, tick)

    # ── Dibujo del brazo ──────────────────────────────────────────────────────

    def _dibujar_brazo(self):
        c = self.canvas
        c.delete("all")
        W = c.winfo_width()
        H = c.winfo_height()
        if W < 10 or H < 10:
            return

        # Fondo + cuadrícula
        c.create_rectangle(0, 0, W, H, fill=COLOR_CANVAS, outline="")
        gc = "#1a1a2e"
        for x in range(0, W, 28):
            c.create_line(x, 0, x, H, fill=gc, width=1)
        for y in range(0, H, 28):
            c.create_line(0, y, W, y, fill=gc, width=1)

        ground_y = H - 40
        c.create_line(20, ground_y, W - 20, ground_y,
                      fill="#2d2d4e", width=1, dash=(4, 6))

        cx = int(W * 0.5)
        cy = ground_y
        L1 = H * 0.28
        L2 = H * 0.20

        ang_h = math.radians(self._anim_h)
        ang_v = math.radians(self._anim_v)

        hx2 = cx + L1 * math.cos(ang_h)
        hy2 = cy - L1 * math.sin(ang_h)

        ang2 = ang_h + (ang_v - math.pi / 2)
        vx = hx2 + L2 * math.cos(ang2)
        vy = hy2 - L2 * math.sin(ang2)

        # ── Base 
        c.create_oval(cx - 44, cy - 14 + 8,
                      cx + 44, cy + 14 + 8,
                      fill="#0a0a16", outline="")
        c.create_oval(cx - 42, cy - 14,
                      cx + 42, cy + 14,
                      fill=ARM_BASE_D, outline=COLOR_ACENTO, width=1)
        c.create_oval(cx - 26, cy - 8,
                      cx + 26, cy + 8,
                      fill=ARM_BASE_L, outline=COLOR_ACENTO2, width=1)
        mx = cx + 18 * math.cos(ang_h)
        my = cy -  6 * math.sin(ang_h)
        c.create_oval(mx - 3, my - 3, mx + 3, my + 3, fill=COLOR_NUM, outline="")
        c.create_text(cx, cy + 2, text="BASE",
                      fill=COLOR_TEXTO, font=("Courier New", 7, "bold"))

        # ── Segmento 1 ───────────────────────────────────────────────────────
        hx1, hy1 = cx, cy - 6

        c.create_line(hx1+2, hy1+3, hx2+2, hy2+3,
                      width=16, fill="#0a0a20", capstyle=tk.ROUND)
        c.create_line(hx1, hy1, hx2, hy2,
                      width=14, fill=ARM_SEG1_DARK, capstyle=tk.ROUND)
        c.create_line(hx1, hy1, hx2, hy2,
                      width=10, fill=ARM_SEG1, capstyle=tk.ROUND)
        ox =  math.sin(ang_h) * 3
        oy =  math.cos(ang_h) * 3
        c.create_line(hx1+ox, hy1+oy, hx2+ox*0.4, hy2+oy*0.4,
                      width=2, fill="#c0f0ff", capstyle=tk.ROUND)
        c.create_line(hx1, hy1, hx2, hy2,
                      width=1, fill="#282a36", dash=(4, 3), capstyle=tk.ROUND)

        # Articulación hombro
        c.create_oval(hx2-11, hy2-11, hx2+11, hy2+11, fill="#3a2800", outline="")
        c.create_oval(hx2-10, hy2-10, hx2+10, hy2+10,
                      fill=ARM_JOINT1, outline=COLOR_NUM, width=1)
        c.create_oval(hx2-4, hy2-4, hx2+4, hy2+4, fill=COLOR_WARN, outline="")

        # ── Segmento 2 ───────────────────────────────────────────────────────
        c.create_line(hx2+2, hy2+3, vx+2, vy+3,
                      width=14, fill="#0a0a20", capstyle=tk.ROUND)
        c.create_line(hx2, hy2, vx, vy,
                      width=12, fill=ARM_SEG2_DARK, capstyle=tk.ROUND)
        c.create_line(hx2, hy2, vx, vy,
                      width=9, fill=ARM_SEG2, capstyle=tk.ROUND)
        ox2 =  math.sin(ang2) * 2.5
        oy2 =  math.cos(ang2) * 2.5
        c.create_line(hx2+ox2, hy2+oy2, vx+ox2*0.3, vy+oy2*0.3,
                      width=2, fill="#90ffb0", capstyle=tk.ROUND)
        c.create_line(hx2, hy2, vx, vy,
                      width=1, fill="#1a3a1a", dash=(4, 3), capstyle=tk.ROUND)

        # Articulación codo
        c.create_oval(vx-9, vy-9, vx+9, vy+9, fill="#300000", outline="")
        c.create_oval(vx-8, vy-8, vx+8, vy+8,
                      fill=ARM_JOINT2, outline=COLOR_WARN, width=1)
        c.create_oval(vx-3, vy-3, vx+3, vy+3, fill="#ff8888", outline="")

        # ── Pinzas ───────────────────────────────────────────────────────────
        apertura  = ((180 - self._anim_p) / 180) * 18
        tip_color = COLOR_OK if self._anim_p < 10 else COLOR_ERROR

        for lado in [1, -1]:
            sa  = ang2 + lado * (0.32 + apertura * 0.012)
            fx1 = vx +  8 * math.cos(sa)
            fy1 = vy -  8 * math.sin(sa)
            fx2 = vx + (22 + apertura) * math.cos(sa)
            fy2 = vy - (22 + apertura) * math.sin(sa)
            c.create_line(fx1+1, fy1+2, fx2+1, fy2+2,
                          width=7, fill="#0a0a16", capstyle=tk.ROUND)
            c.create_line(fx1, fy1, fx2, fy2,
                          width=5, fill="#c8a800", capstyle=tk.ROUND)
            c.create_line(fx1, fy1, fx2, fy2,
                          width=3, fill=ARM_GRIPPER, capstyle=tk.ROUND)
            c.create_oval(fx2-5, fy2-5, fx2+5, fy2+5, fill=tip_color, outline="")

        pb1x = vx - 7 * math.sin(ang2)
        pb1y = vy + 7 * math.cos(ang2)
        pb2x = vx + 7 * math.sin(ang2)
        pb2y = vy - 7 * math.cos(ang2)
        c.create_line(pb1x, pb1y, pb2x, pb2y, width=5, fill="#888888", capstyle=tk.ROUND)
        c.create_line(pb1x, pb1y, pb2x, pb2y, width=3, fill="#aaaaaa", capstyle=tk.ROUND)

        # ── HUD ──────────────────────────────────────────────────────────────
        p = int(self._anim_p)
        hud = [
            (f"Pinza:  {p:>3}°",
             COLOR_OK if p < 10 else (COLOR_ERROR if p >= 170 else COLOR_WARN)),
            (f"Base:   {self.estado['brazo_h']:>3}°",       COLOR_KW),
            (f"Brazo:  {self.estado['brazo_v']:>3}°",       COLOR_KW),
            (f"Vel:    {self.estado.get('velocidad','?')}", COLOR_ACENTO),
        ]
        for i, (txt, col) in enumerate(hud):
            x0, y0 = 10, 10 + i * 18
            c.create_rectangle(x0, y0, x0 + len(txt)*7 + 8, y0 + 14,
                                fill="#0a0a16", outline="#2d2d4e", width=1)
            c.create_text(x0 + 4, y0 + 7, anchor="w",
                          text=txt, fill=col,
                          font=("Courier New", 9, "bold"))

        if self.ejecutando:
            c.create_oval(W-22, 10, W-10, 22, fill=COLOR_OK, outline="")
            c.create_text(W-26, 16, anchor="e",
                          text="EJECUTANDO", fill=COLOR_OK,
                          font=("Courier New", 8, "bold"))
        if self.modo_fisico:
            c.create_text(W-8, H-10, anchor="se",
                          text="ESP32 CONECTADO", fill=COLOR_OK,
                          font=("Courier New", 8))

    # ── Lógica de estado ───────────────────────────────────────────────────────

    def _actualizar_estado_ui(self):
        p    = self.estado['pinza']
        txt  = "ABIERTA" if p == 0 else ("CERRADA" if p >= 170 else "PARCIAL")
        col  = COLOR_OK if p == 0 else (COLOR_ERROR if p >= 170 else COLOR_WARN)
        self.lbl_pinza.config(text=f"{p}° {txt}", fg=col)
        self.lbl_h.config(text=f"{self.estado['brazo_h']}°")
        self.lbl_v.config(text=f"{self.estado['brazo_v']}°")
        self.lbl_vel.config(text=self.estado.get('velocidad', 'NORMAL'))
        self._dibujar_brazo()

    # ── Conexión ESP32 

    def _conectar_brazo(self):
        if self.modo_fisico:
            self._log("⚠ Ya hay un brazo conectado\n")
            return
        self._log("🔌 Conectando al brazo físico ESP32...\n")
        self.brazo = BrazoESP32(puerto="COM7")
        if self.brazo.conectar():
            self.modo_fisico = True
            self.lbl_conexion.config(text="⬤  ESP32 CONECTADO", fg=COLOR_OK)
            self._log("✅ Brazo robótico ESP32 conectado\n")
            self.brazo.estado()
        else:
            self.brazo = None
            self.lbl_conexion.config(text="⬤  SIMULACIÓN", fg=COLOR_WARN)
            self._log("⚠ No se pudo conectar. Modo simulación.\n")

    def _desconectar_brazo(self):
        if self.brazo:
            self.brazo.desconectar()
            self.brazo = None
        self.modo_fisico = False
        self.lbl_conexion.config(text="⬤  SIMULACIÓN", fg=COLOR_WARN)
        self._log("🔌 Brazo físico desconectado\n")

    # ── Ejecución ──────────────────────────────────────────────────────────────

    def _ejecutar_codigo(self):
        if self.ejecutando:
            self._log("⚠ Ya hay una ejecución en curso\n")
            return
        self.ejecutando = True
        threading.Thread(target=self._ejecutar_en_hilo, daemon=True).start()

    def _detener_ejecucion(self):
        self.ejecutando = False
        self._log("■ Ejecución detenida\n")

    def _ejecutar_en_hilo(self):
        try:
            codigo = self.text_code.get("1.0", "end-1c")
            self.text_errors.delete("1.0", "end")
            self.text_console.delete("1.0", "end")

            self._log("═" * 52 + "\n")
            self._log("  HAWKE — COMPILADOR EN EJECUCIÓN\n")
            self._log("═" * 52 + "\n\n")

            if not self.ejecutando:
                return

            # Fase 1: Léxico
            self._log("🔍 FASE 1: ANÁLISIS LÉXICO\n")
            self._log("─" * 36 + "\n")
            lexer = Lexer(codigo)
            tokens, pila_lex = lexer.obtener_tokens()
            self._log(f"  ✓ {len(tokens)} tokens encontrados\n\n")
            for i, tok in enumerate(tokens[:15], 1):
                self._log(f"   {i:>2}. {tok[0]:<15} '{tok[1]}' (L{tok[2]}, C{tok[3]})\n")
            if len(tokens) > 15:
                self._log(f"   ... y {len(tokens)-15} más\n")
            self._log("\n")

            if pila_lex.hay_errores():
                self._mostrar_errores(pila_lex, "LÉXICOS")
                self._log("✖ DETENIDO — ERRORES LÉXICOS\n")
                return

            if not self.ejecutando:
                return

            # Fase 2: Parser
            self._log("🔍 FASE 2: ANÁLISIS SINTÁCTICO\n")
            self._log("─" * 36 + "\n")
            parser = Parser(tokens)
            instrucciones, pila_par = parser.parse()
            self._log(f"  ✓ {len(instrucciones)} instrucciones reconocidas\n\n")
            for i, inst in enumerate(instrucciones, 1):
                self._log(f"   {i:>2}. {inst}\n")
            self._log("\n")

            if pila_par.hay_errores():
                self._mostrar_errores(pila_par, "SINTÁCTICOS/SEMÁNTICOS")
                self._log("✖ DETENIDO — ERRORES SINTÁCTICOS\n")
                return

            if not self.ejecutando:
                return

            # Fase 3: Ejecución
            self._log("🚀 FASE 3: EJECUCIÓN\n")
            self._log("─" * 36 + "\n")
            self._log("▶ Iniciando programa...\n\n")
            self._ejecutar_instrucciones(instrucciones, parser.tabla_sim)

            if self.ejecutando:
                self._log("\n✅ PROGRAMA FINALIZADO SIN ERRORES\n")
                self.text_errors.delete("1.0", "end")
                self.text_errors.insert("end",
                    "✅ No se encontraron errores\n\n"
                    "  Análisis léxico, sintáctico y semántico correctos.\n"
                    "  Ejecución completada exitosamente.\n")

        except Exception as e:
            self._log(f"\n✖ ERROR INESPERADO: {e}\n")
            import traceback
            traceback.print_exc()
            self.text_errors.delete("1.0", "end")
            self.text_errors.insert("end", f"✖ ERROR INESPERADO: {e}\n")
        finally:
            self.ejecutando = False

    def _ejecutar_instrucciones(self, instrucciones, tabla_sim, indent=0):
        pre = "  " * indent
        for inst in instrucciones:
            if not self.ejecutando:
                return
            cmd = inst[0]

            if cmd == 'ABRIR':
                self.estado['pinza'] = 0
                self._log(f"{pre}→ ABRIR pinzas\n")
                if self.modo_fisico and self.brazo:
                    self.brazo.abrir()

            elif cmd == 'CERRAR':
                self.estado['pinza'] = 180
                self._log(f"{pre}→ CERRAR pinzas\n")
                if self.modo_fisico and self.brazo:
                    self.brazo.cerrar()

            elif cmd == 'MOVER':
                _, angulo, vel = inst
                self.estado['brazo_v']   = angulo
                self.estado['velocidad'] = vel
                self._log(f"{pre}→ MOVER brazo a {angulo}° [{vel}]\n")
                if self.modo_fisico and self.brazo:
                    self.brazo.mover(angulo)

            elif cmd == 'GIRAR':
                _, direccion, angulo, vel = inst
                self.estado['brazo_h']   = angulo
                self.estado['velocidad'] = vel
                self._log(f"{pre}→ GIRAR {direccion} {angulo}° [{vel}]\n")
                if self.modo_fisico and self.brazo:
                    self.brazo.girar(direccion, angulo)

            elif cmd == 'ESPERAR':
                _, ms = inst
                self._log(f"{pre}→ ESPERAR {ms} ms\n")
                if self.modo_fisico and self.brazo:
                    time.sleep(ms / 1000)

            elif cmd == 'GUARDAR':
                _, nombre, _ = inst
                self._log(f"{pre}→ GUARDAR rutina '{nombre}'\n")

            elif cmd == 'EJECUTAR':
                _, nombre = inst
                rutina = tabla_sim.obtener_rutina(nombre)
                if rutina:
                    self._log(f"{pre}→ EJECUTAR '{nombre}':\n")
                    self._ejecutar_instrucciones(rutina, tabla_sim, indent + 1)
                else:
                    self._log(f"{pre}→ ERROR: rutina '{nombre}' no definida\n")

            elif cmd == 'REPETIR':
                _, n, bloque = inst
                self._log(f"{pre}→ REPETIR {n} veces:\n")
                for i in range(n):
                    if not self.ejecutando:
                        return
                    self._log(f"{pre}  Iteración {i+1}/{n}\n")
                    self._ejecutar_instrucciones(bloque, tabla_sim, indent + 1)

            elif cmd == 'HOME':
                self.estado['brazo_h']   = 90
                self.estado['brazo_v']   = 45
                self.estado['pinza']     = 0
                self.estado['velocidad'] = 'NORMAL'
                self._log(f"{pre}→ HOME (posición de reposo)\n")
                if self.modo_fisico and self.brazo:
                    self.brazo.home()

            self._actualizar_estado_ui()
            self.root.update_idletasks()

    def _mostrar_errores(self, pila, titulo):
        self.text_errors.delete("1.0", "end")
        self.text_errors.insert("end", f"═══ Errores {titulo} ═══\n\n")
        for e in pila.pila:
            self.text_errors.insert("end",
                f"[{e.tipo}] L{e.linea}:C{e.columna}  '{e.token}'\n")
            self.text_errors.insert("end", f"  → {e.descripcion}\n")
            self.text_errors.insert("end", f"  💡 {e.solucion}\n\n")
        self.text_errors.see("end")

    def _log(self, texto):
        try:
            self.text_console.insert("end", texto)
            self.text_console.see("end")
        except Exception:
            pass
        print(texto, end="")

    # ── Tabla de símbolos ──────────────────────────────────────────────────────

    def _mostrar_tabla_simbolos(self):
        codigo = self.text_code.get("1.0", "end-1c")
        lexer  = Lexer(codigo)
        tokens, pila_lex = lexer.obtener_tokens()
        if pila_lex.hay_errores():
            self._mostrar_errores(pila_lex, "LÉXICOS")
            return
        parser = Parser(tokens)
        instrucciones, pila_par = parser.parse()
        if pila_par.hay_errores():
            self._mostrar_errores(pila_par, "SINTÁCTICOS/SEMÁNTICOS")
            return
        tabla = parser.tabla_sim

        win = tk.Toplevel(self.root)
        win.title("HAWKE — Tabla de Símbolos")
        win.geometry("800x560")
        win.configure(bg=COLOR_BG)
        win.transient(self.root)
        win.grab_set()

        tk.Frame(win, bg=COLOR_PANEL2).pack(fill="x")
        tk.Label(win, text=" 📋  TABLA DE SÍMBOLOS ",
                 bg=COLOR_PANEL2, fg=COLOR_ACENTO,
                 font=("Courier New", 11, "bold"),
                 padx=10, pady=8).pack(fill="x")
        tk.Frame(win, bg=COLOR_BORDE, height=1).pack(fill="x")

        f = tk.Frame(win, bg=COLOR_BG)
        f.pack(fill="both", expand=True, padx=10, pady=10)

        sy = tk.Scrollbar(f, orient="vertical",   bg=COLOR_PANEL, troughcolor=COLOR_BG)
        sx = tk.Scrollbar(f, orient="horizontal", bg=COLOR_PANEL, troughcolor=COLOR_BG)
        sy.pack(side="right", fill="y")
        sx.pack(side="bottom", fill="x")

        ta = tk.Text(f, font=("Courier New", 10),
                     bg=COLOR_CANVAS, fg=COLOR_TEXTO,
                     relief="flat", padx=10, pady=10,
                     yscrollcommand=sy.set, xscrollcommand=sx.set,
                     wrap="none")
        ta.pack(fill="both", expand=True)
        sy.config(command=ta.yview)
        sx.config(command=ta.xview)

        SEP  = "═" * 80
        sep2 = "─" * 80
        out  = (f"{SEP}\n"
                f"  {'Lexema':<20} {'Token':<20} {'Línea':<8} {'Col':<8} Contexto\n"
                f"{sep2}\n")
        for s in tabla.simbolos:
            out += (f"  {s['lexema']:<20} {s['token']:<20}"
                    f" {s['linea']:<8} {s['columna']:<8} {s['contexto']}\n")
        out += f"{SEP}\n  Total: {len(tabla.simbolos)} símbolo(s)\n"

        if tabla.rutinas:
            out += (f"\n{SEP}\n  RUTINAS GUARDADAS\n{sep2}\n"
                    f"  {'Nombre':<20} {'Línea':<8} Instrucciones\n{sep2}\n")
            for nombre, info in tabla.rutinas.items():
                out += (f"  {nombre:<20} {info['linea']:<8}"
                        f" {len(info['instrucciones'])} instrucción(es)\n")
            out += f"{SEP}\n"

        ta.insert("1.0", out)
        ta.config(state="disabled")

        tk.Button(win, text="Cerrar", command=win.destroy,
                  bg=COLOR_ACENTO, fg="#1a1a2e",
                  font=("Courier New", 9, "bold"),
                  relief="flat", padx=24, pady=6,
                  cursor="hand2").pack(pady=8)

    # ── Nuevo archivo ─────────────────────────────────────────────────────────

    def _nuevo_archivo(self):
        """Crea un nuevo archivo vacío."""
        if messagebox.askyesno("Nuevo archivo", "¿Limpiar el editor? Los cambios no guardados se perderán."):
            self.text_code.delete("1.0", "end")
            self.text_code.insert("1.0", "")
            self._update_line_nums()
            self._log("📄 Nuevo archivo creado\n")

    # ── Guardar como ─────────────────────────────────────────────────────────

    def _guardar_como(self):
        """Guarda el archivo con un nombre diferente."""
        ruta = filedialog.asksaveasfilename(
            title="Guardar archivo HAWKE como",
            defaultextension=".hwk",
            filetypes=[
                ("Archivos HAWKE", "*.hawke"),
                ("Archivos HWK", "*.hwk"),
                ("Texto", "*.txt")
            ]
        )
        if ruta:
            try:
                with open(ruta, "w", encoding="utf-8") as f:
                    f.write(self.text_code.get("1.0", "end-1c"))
                self._log(f"💾 Archivo guardado como: {ruta}\n")
            except Exception as e:
                self._log(f"❌ Error al guardar: {e}\n")

    # ── Ejemplo inicial ────────────────────────────────────────────────────────

    def _cargar_ejemplo(self):
        codigo = (
            'GUARDAR AGARRAR {\n'
            '    MOVER 30 LENTO;\n'
            '    CERRAR;\n'
            '    ESPERAR 500;\n'
            '    MOVER 90 RAPIDO;\n'
            '};\n\n'
            'EJECUTAR AGARRAR;\n'
            'GIRAR DERECHA 45;\n'
            'ESPERAR 1000;\n'
            'ABRIR;\n'
            'HOME;\n'
        )
        self.text_code.insert("1.0", codigo)
        self._update_line_nums()

    # ── Archivo ────────────────────────────────────────────────────────────────

    def _abrir_archivo(self):
        """Abre un archivo .hawke o .hwk desde el sistema."""
        ruta = filedialog.askopenfilename(
            title="Abrir archivo HAWKE",
            filetypes=[
                ("Archivos HAWKE", "*.hawke *.hwk"),
                ("Archivos HAWKE", "*.hawke"),
                ("Archivos HWK", "*.hwk"),
                ("Texto", "*.txt"),
                ("Todos los archivos", "*.*")
            ]
        )
        if ruta:
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    contenido = f.read()
                self.text_code.delete("1.0", "end")
                self.text_code.insert("1.0", contenido)
                self._update_line_nums()
                self._log(f"📂 Archivo abierto: {ruta}\n")
            except Exception as e:
                self._log(f"❌ Error al abrir: {e}\n")

    def _guardar_archivo(self):
        """Guarda el archivo actual."""
        ruta = filedialog.asksaveasfilename(
            title="Guardar archivo HAWKE",
            defaultextension=".hwk",
            filetypes=[
                ("Archivos HAWKE", "*.hawke"),
                ("Archivos HWK", "*.hwk"),
                ("Texto", "*.txt")
            ]
        )
        if ruta:
            try:
                with open(ruta, "w", encoding="utf-8") as f:
                    f.write(self.text_code.get("1.0", "end-1c"))
                self._log(f"💾 Archivo guardado: {ruta}\n")
            except Exception as e:
                self._log(f"❌ Error al guardar: {e}\n")

    def _limpiar_todo(self):
        self.text_code.delete("1.0", "end")
        self.text_errors.delete("1.0", "end")
        self.text_console.delete("1.0", "end")
        self.estado = {'pinza': 0, 'brazo_h': 90, 'brazo_v': 45, 'velocidad': 'NORMAL'}
        self._update_line_nums()
        self._actualizar_estado_ui()
        self._log("🗑 Todo limpiado\n")
        self.text_errors.insert("end", "✅ Panel limpiado. Esperando ejecución...\n")

    # ── About ──────────────────────────────────────────────────────────────────

    def _mostrar_about(self):
        """Ventana 'Acerca de' con información del software y autores."""
        win = tk.Toplevel(self.root)
        win.title("Acerca de HAWKE")
        win.geometry("700x850")
        win.configure(bg=COLOR_BG)
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()

        # Encabezado con color de acento
        hdr = tk.Frame(win, bg=COLOR_ACENTO2, pady=2)
        hdr.pack(fill="x")
        tk.Label(hdr, text="⬡  HAWKE",
                 bg=COLOR_ACENTO2, fg=COLOR_BG,
                 font=("Courier New", 26, "bold"),
                 pady=20).pack()

        body = tk.Frame(win, bg=COLOR_PANEL, pady=16, padx=30)
        body.pack(fill="both", expand=True)

        def lbl(txt, fg=COLOR_TEXTO, font_size=9, bold=False):
            weight = "bold" if bold else "normal"
            tk.Label(body, text=txt, bg=COLOR_PANEL, fg=fg,
                     font=("Courier New", font_size, weight),
                     anchor="w", justify="left").pack(fill="x", pady=1)

        # ========== TÍTULO ==========
        lbl("Control de Brazo Robótico — Lenguaje HAWKE",
            fg=COLOR_ACENTO, font_size=11, bold=True)
        lbl("")

        # ========== INFORMACIÓN GENERAL ==========
        lbl("INFORMACIÓN GENERAL", fg=COLOR_KW, bold=True)
        lbl(f"{'Versión:':<15} 2.0", fg=COLOR_NUM)
        lbl(f"{'Lenguaje:':<15} Python 3 + Tkinter", fg=COLOR_TEXTO2)
        lbl(f"{'Hardware:':<15} ESP32 (opcional — modo simulación)", fg=COLOR_TEXTO2)
        lbl(f"{'Inicio:':<15} Marzo 2025", fg=COLOR_TEXTO2)
        lbl(f"{'Entrega final:':<15} Junio 2025", fg=COLOR_TEXTO2)
        lbl("")

        # ========== COMPILADOR ==========
        tk.Frame(body, bg=COLOR_BORDE, height=1).pack(fill="x", pady=6)
        lbl("COMPILADOR HAWKE", fg=COLOR_KW, bold=True)
        lbl("  • Análisis Léxico      — Lexer (AFD con matriz de transición)", fg=COLOR_TEXTO2)
        lbl("  • Análisis Sintáctico  — Parser (recursivo descendente)", fg=COLOR_TEXTO2)
        lbl("  • Tabla de Símbolos    — TablaSimbolos", fg=COLOR_TEXTO2)
        lbl("  • Gestión de Errores   — PilaErrores", fg=COLOR_TEXTO2)
        lbl("")

        # ========== COMANDOS ==========
        tk.Frame(body, bg=COLOR_BORDE, height=1).pack(fill="x", pady=6)
        lbl("COMANDOS DISPONIBLES", fg=COLOR_KW, bold=True)
        lbl("  ABRIR, CERRAR, MOVER, GIRAR, ESPERAR", fg=COLOR_TEXTO2)
        lbl("  REPETIR, GUARDAR, EJECUTAR, HOME", fg=COLOR_TEXTO2)
        lbl("")

        # ========== ALUMNO ==========
        tk.Frame(body, bg=COLOR_BORDE, height=1).pack(fill="x", pady=6)
        lbl("ALUMNO", fg=COLOR_KW, bold=True)
        lbl(f"{'Nombre:':<15} César Eduardo Martínez Arredondo", fg=COLOR_NUM)
        lbl(f"{'Carrera:':<15} Ing. en Sistemas Computacionales", fg=COLOR_TEXTO2)
        lbl(f"{'Materia:':<15} Lenguajes y Autómatas II", fg=COLOR_TEXTO2)
        lbl(f"{'Profesor:':<15} RICARDO González González", fg=COLOR_TEXTO2)
        lbl(f"{'Grupo:':<15} A", fg=COLOR_TEXTO2)
        lbl(f"{'Institución:':<15} TecNM Campus Celaya", fg=COLOR_TEXTO2)
        lbl("")

        #  LOGROS 
        tk.Frame(body, bg=COLOR_BORDE, height=1).pack(fill="x", pady=6)
        lbl("LOGROS DEL PROYECTO", fg=COLOR_KW, bold=True)
        lbl("  • Lenguaje de programación funcional", fg=COLOR_OK)
        lbl("  • Interfaz gráfica completa con Tkinter", fg=COLOR_OK)
        lbl("  • Control de brazo físico vía ESP32", fg=COLOR_OK)
        lbl("  • Simulación en tiempo real con animación suave", fg=COLOR_OK)
        lbl("  • Tabla de símbolos visual", fg=COLOR_OK)
        lbl("  • Clasificación completa de errores", fg=COLOR_OK)
        lbl("")

        #  CRÉDITOS 
        tk.Frame(body, bg=COLOR_BORDE, height=1).pack(fill="x", pady=6)
        lbl("Desarrollado con fines académicos.", fg=COLOR_TEXTO2)
        lbl("Tecnológico Nacional de México en Celaya", fg=COLOR_TEXTO2)
        lbl("Todos los derechos reservados © 2026", fg=COLOR_TEXTO2)

        # Botón cerrar
        tk.Button(win, text="  Cerrar  ", command=win.destroy,
                  bg=COLOR_ACENTO, fg=COLOR_BG,
                  font=("Courier New", 9, "bold"),
                  relief="flat", padx=20, pady=6,
                  cursor="hand2").pack(pady=12)

    # ── Documentación 

    def _mostrar_documentacion(self):
        """Ventana de documentación completa del lenguaje HAWKE."""
        win = tk.Toplevel(self.root)
        win.title("HAWKE — Documentación del Lenguaje")
        win.geometry("760x600")
        win.configure(bg=COLOR_BG)
        win.transient(self.root)
        win.grab_set()

        hdr = tk.Frame(win, bg=COLOR_PANEL2)
        hdr.pack(fill="x")
        tk.Label(hdr, text=" 📖  DOCUMENTACIÓN DEL LENGUAJE HAWKE ",
                 bg=COLOR_PANEL2, fg=COLOR_ACENTO,
                 font=("Courier New", 11, "bold"),
                 padx=10, pady=10).pack(side="left")
        tk.Frame(win, bg=COLOR_BORDE, height=1).pack(fill="x")

        f = tk.Frame(win, bg=COLOR_BG)
        f.pack(fill="both", expand=True, padx=10, pady=10)

        sy = tk.Scrollbar(f, orient="vertical",   bg=COLOR_PANEL, troughcolor=COLOR_BG)
        sx = tk.Scrollbar(f, orient="horizontal", bg=COLOR_PANEL, troughcolor=COLOR_BG)
        sy.pack(side="right", fill="y")
        sx.pack(side="bottom", fill="x")

        ta = tk.Text(f, font=("Courier New", 10),
                     bg=COLOR_CANVAS, fg=COLOR_TEXTO,
                     relief="flat", padx=14, pady=12,
                     yscrollcommand=sy.set, xscrollcommand=sx.set,
                     wrap="none")
        ta.pack(fill="both", expand=True)
        sy.config(command=ta.yview)
        sx.config(command=ta.xview)

        ta.tag_config("titulo",    foreground=COLOR_ACENTO,  font=("Courier New", 11, "bold"))
        ta.tag_config("subtitulo", foreground=COLOR_KW,      font=("Courier New", 10, "bold"))
        ta.tag_config("kw",        foreground=COLOR_KW,      font=("Courier New", 10, "bold"))
        ta.tag_config("num",       foreground=COLOR_NUM)
        ta.tag_config("ok",        foreground=COLOR_OK)
        ta.tag_config("warn",      foreground=COLOR_WARN)
        ta.tag_config("dim",       foreground=COLOR_TEXTO2)
        ta.tag_config("sep",       foreground=COLOR_BORDE2)

        def ins(txt, tag=None):
            ta.insert("end", txt, tag or "")

        SEP  = "═" * 70 + "\n"
        sep2 = "─" * 70 + "\n"

        ins(SEP, "sep")
        ins("  HAWKE — Lenguaje de Control de Brazo Robótico  v2.0\n", "titulo")
        ins(SEP, "sep")
        ins("\n")

        ins("  DESCRIPCIÓN GENERAL\n", "subtitulo")
        ins(sep2, "sep")
        ins("  HAWKE es un lenguaje de dominio específico (DSL) diseñado para\n", "dim")
        ins("  programar movimientos de un brazo robótico de forma legible.\n", "dim")
        ins("  El compilador pasa por tres fases: léxico, sintáctico y ejecución.\n\n", "dim")

        ins("  INSTRUCCIONES DISPONIBLES\n", "subtitulo")
        ins(sep2, "sep")

        instrucciones = [
            ("ABRIR",
             "Abre las pinzas del brazo (posición 0°, máxima separación).",
             "ABRIR;"),
            ("CERRAR",
             "Cierra completamente las pinzas (posición 180°, dedos juntos).",
             "CERRAR;"),
            ("MOVER <ángulo> [velocidad]",
             "Mueve el brazo vertical al ángulo indicado (0°–180°).\n"
             "  Velocidades: LENTO | NORMAL | RAPIDO  (opcional, default NORMAL).",
             "MOVER 45 LENTO;\nMOVER 90;"),
            ("GIRAR <dirección> <ángulo> [velocidad]",
             "Gira la base horizontal.\n"
             "  Dirección: IZQUIERDA | DERECHA\n"
             "  Ángulo: 0°–180°\n"
             "  Velocidades: LENTO | NORMAL | RAPIDO  (opcional).",
             "GIRAR DERECHA 90;\nGIRAR IZQUIERDA 45 RAPIDO;"),
            ("ESPERAR <ms>",
             "Pausa la ejecución el número de milisegundos indicado.",
             "ESPERAR 1000;"),
            ("HOME",
             "Regresa el brazo a la posición de reposo:\n"
             "  Base=90°, Brazo=45°, Pinza=0° (abierta), Velocidad=NORMAL.",
             "HOME;"),
            ("GUARDAR <nombre> { ... }",
             "Define y guarda una rutina con nombre para reutilizarla.\n"
             "  Las instrucciones van dentro de llaves { }.",
             "GUARDAR RECOGER {\n    MOVER 30 LENTO;\n    CERRAR;\n    MOVER 90;\n};"),
            ("EJECUTAR <nombre>",
             "Ejecuta una rutina previamente guardada con GUARDAR.",
             "EJECUTAR RECOGER;"),
            ("REPETIR <n> { ... }",
             "Repite el bloque de instrucciones n veces.",
             "REPETIR 3 {\n    ABRIR;\n    ESPERAR 300;\n    CERRAR;\n};"),
        ]

        for nombre, desc, ejemplo in instrucciones:
            ins(f"\n  ", "dim")
            ins(f"{nombre}\n", "kw")
            for linea in desc.split("\n"):
                ins(f"    {linea}\n", "dim")
            ins("    Ejemplo:\n", "dim")
            for linea in ejemplo.split("\n"):
                ins(f"      {linea}\n", "num")

        ins("\n")
        ins(SEP, "sep")
        ins("  VELOCIDADES\n", "subtitulo")
        ins(sep2, "sep")
        ins("  LENTO   → movimiento suave, mayor precisión\n", "dim")
        ins("  NORMAL  → velocidad estándar (valor por defecto)\n", "dim")
        ins("  RAPIDO  → movimiento rápido, menor precisión\n\n", "dim")

        ins(SEP, "sep")
        ins("  ESTRUCTURA DE UN PROGRAMA HAWKE\n", "subtitulo")
        ins(sep2, "sep")
        ins("  -- Definir rutinas al inicio (opcional)\n", "dim")
        ins("  GUARDAR MI_RUTINA {\n", "num")
        ins("      MOVER 30 LENTO;\n", "num")
        ins("      CERRAR;\n", "num")
        ins("      ESPERAR 500;\n", "num")
        ins("  };\n\n", "num")
        ins("  -- Programa principal\n", "dim")
        ins("  EJECUTAR MI_RUTINA;\n", "num")
        ins("  GIRAR DERECHA 90 NORMAL;\n", "num")
        ins("  ABRIR;\n", "num")
        ins("  HOME;\n\n", "num")

        ins(SEP, "sep")
        ins("  NOTAS\n", "subtitulo")
        ins(sep2, "sep")
        ins("  • Cada instrucción termina con punto y coma  ;\n", "warn")
        ins("  • Las instrucciones deben escribirse en MAYÚSCULAS (ej: ABRIR, no abrir).\n", "warn")
        ins("  • En modo simulación el ESP32 no es necesario.\n", "ok")
        ins("  • Usar F5 o el botón ▶ Ejecutar para correr el programa.\n", "ok")
        ins(SEP, "sep")

        ta.config(state="disabled")
        ta.see("1.0")

        tk.Button(win, text="  Cerrar  ", command=win.destroy,
                  bg=COLOR_ACENTO, fg=COLOR_BG,
                  font=("Courier New", 9, "bold"),
                  relief="flat", padx=20, pady=6,
                  cursor="hand2").pack(pady=8)

    def _salir(self):
        self._anim_on = False
        if self.brazo:
            self.brazo.desconectar()
        self.root.quit()


# ── Punto de entrada 

if __name__ == "__main__":
    root = tk.Tk()
    app  = AppHAWKE(root)
    root.mainloop() 