
#  HAWKE - Analizador Lexico (Lexer)
#  Convierte codigo fuente en una lista de tokens


import re
from pila_errores import PilaErrores, Error



# Comandos que esperan un angulo (rango 0-180) despues de ellos
COMANDOS_ANGULO = {'KW_MOVER', 'KW_GIRAR'}


class Lexer:
    """
    Analizador lexico para el lenguaje HAWKE.
    Convierte codigo fuente en una lista de tokens.
    """

    def __init__(self, codigo):
        """
        Inicializa el lexer con el codigo fuente a analizar.

        Parametros:
        codigo (str): Codigo fuente completo del programa HAWKE
        """
        self.codigo       = codigo
        self.posicion     = 0
        self.linea        = 1
        self.columna      = 1
        self.pila_errores = PilaErrores()
        self._ultimo_kw   = None   # rastrea el comando anterior para validar angulos

        # PATRONES DE TOKENS
        # Orden importa: palabras reservadas antes que IDENTIFICADOR y NUMERO
        self.patrones = [
            ('KW_ABRIR',      r'ABRIR\b'),
            ('KW_CERRAR',     r'CERRAR\b'),
            ('KW_MOVER',      r'MOVER\b'),
            ('KW_GIRAR',      r'GIRAR\b'),
            ('KW_ESPERAR',    r'ESPERAR\b'),
            ('KW_REPETIR',    r'REPETIR\b'),
            ('KW_GUARDAR',    r'GUARDAR\b'),
            ('KW_EJECUTAR',   r'EJECUTAR\b'),
            ('KW_IZQUIERDA',  r'IZQUIERDA\b'),
            ('KW_DERECHA',    r'DERECHA\b'),
            ('KW_LENTO',      r'LENTO\b'),
            ('KW_NORMAL',     r'NORMAL\b'),
            ('KW_RAPIDO',     r'RAPIDO\b'),
            ('IDENTIFICADOR', r'[A-Z][A-Z0-9_]*'),   # nombres de rutinas
            ('MINUSCULAS',    r'[a-z][a-zA-Z0-9_]*'), # error E002
            ('PUNTO_COMA',    r';'),
            ('LLAVE_ABR',     r'\{'),
            ('LLAVE_CER',     r'\}'),
            ('NUMERO',        r'\d+'),
            ('NUEVA_LINEA',   r'\n'),
            ('ESPACIO',       r'[ \t]+'),
            ('ILEGAL',        r'.'),
        ]

        self.regex_compilado = re.compile(
            '|'.join(f'(?P<{nombre}>{patron})' for nombre, patron in self.patrones)
        )

    def actualizar_linea_columna(self, texto):
        """Actualiza linea y columna al procesar espacios y saltos de linea."""
        for char in texto:
            if char == '\n':
                self.linea  += 1
                self.columna = 1
            else:
                self.columna += 1

    def obtener_tokens(self):
        """
        Analiza el codigo fuente y retorna tokens y errores.

        Retorna:
        tuple: (lista_de_tokens, pila_de_errores)
        Un token es una tupla: (tipo, valor, linea, columna)
        """
        tokens = []

        for match in self.regex_compilado.finditer(self.codigo):
            tipo  = match.lastgroup
            valor = match.group()
            col   = self.columna
            lin   = self.linea

            # ── Ignorar espacios y saltos de linea ──────────────────────
            if tipo in ('ESPACIO', 'NUEVA_LINEA'):
                self.actualizar_linea_columna(valor)
                continue

            # ── Error E001: caracter ilegal ──────────────────────────────
            if tipo == 'ILEGAL':
                self.pila_errores.push(Error(
                    lin, col, valor,
                    f"Caracter '{valor}' no pertenece al alfabeto de HAWKE.",
                    "LEXICO",
                    "Elimine el caracter o revise la instruccion"
                ))
                self.columna += 1
                continue

            # ── Error E002: palabra en minusculas ────────────────────────
            if tipo == 'MINUSCULAS':
                self.pila_errores.push(Error(
                    lin, col, valor,
                    f"Palabra '{valor}' en minusculas. HAWKE solo acepta MAYUSCULAS.",
                    "LEXICO",
                    f"Escriba '{valor.upper()}' en lugar de '{valor}'"
                ))
                self.columna += len(valor)
                continue

            # ── Validacion de angulo (solo despues de MOVER o GIRAR) ─────
            if tipo == 'NUMERO':
                num = int(valor)
                if self._ultimo_kw in COMANDOS_ANGULO:
                    if num < 0 or num > 180:
                        self.pila_errores.push(Error(
                            lin, col, valor,
                            f"Angulo {num} fuera del rango permitido (0-180 grados).",
                            "SEMANTICO",
                            "Use un valor entre 0 y 180 grados"
                        ))
                        self.columna += len(valor)
                        self._ultimo_kw = None
                        continue
                self._ultimo_kw = None  # reset despues de consumir el numero

            # ── Rastrear ultimo comando para validar angulo despues ───────
            if tipo in COMANDOS_ANGULO:
                self._ultimo_kw = tipo
            elif tipo not in ('LLAVE_ABR', 'LLAVE_CER', 'PUNTO_COMA'):
                # Si no es un simbolo de bloque, resetear (el angulo debe ser inmediato)
                if tipo not in ('KW_IZQUIERDA', 'KW_DERECHA'):
                    if tipo != 'NUMERO':
                        self._ultimo_kw = None

            token = (tipo, valor, lin, col)
            tokens.append(token)
            self.columna += len(valor)

        return tokens, self.pila_errores