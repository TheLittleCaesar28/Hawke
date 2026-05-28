#HAWKE - Analizador Léxico con Autómata Finito Determinista (AFD)
#  Matriz de transición

from pila_errores import PilaErrores, Error


#  ÍNDICES DE CATEGORÍAS  (columnas)

C_MAY = 0   # A-Z
C_DIG = 1   # 0-9
C_SEP = 2   # espacio, tab, \n, ;, {, }
C_ERR = 3   # cualquier otro carácter

NUM_CATS = 4



#  ÍNDICES DE ESTADOS  (filas)
Q0 = 0   # inicial
Q1 = 1   # leyendo A-Z (solo letras desde q0)
Q2 = 2   # leyendo letra|dígito mezclados
Q3 = 3   # leyendo dígitos
QF = 4   # final / aceptor
QE = 5   # error

NUM_STATES = 6

# Nombres de los estados para mostrar en logs
NOMBRE_ESTADO = {
    Q0: "Q0(inicio)",
    Q1: "Q1(letra)",
    Q2: "Q2(mezcla)",
    Q3: "Q3(dígito)",
    QF: "QF(final)",
    QE: "QE(error)"
}


#  SEPARADORES
SEPARADORES = {' ', '\t', '\n', ';', '{', '}'}

TOKEN_SEPARADOR = {
    ';': 'PUNTO_COMA',
    '{': 'LLAVE_ABR',
    '}': 'LLAVE_CER',
}


# 
#  MATRIZ DE TRANSICIÓN
TRANS = [
    [Q1, Q3, QF, QE],  # Q0
    [Q1, Q2, QF, QE],  # Q1
    [Q2, Q2, QF, QE],  # Q2
    [QE, Q3, QF, QE],  # Q3
    [Q0, Q0, Q0, Q0],  # QF
    [Q0, Q0, Q0, Q0],  # QE
]


#  PALABRAS RESERVADAS
PALABRAS_RESERVADAS = {
    'ABRIR':     'KW_ABRIR',
    'CERRAR':    'KW_CERRAR',
    'MOVER':     'KW_MOVER',
    'GIRAR':     'KW_GIRAR',
    'ESPERAR':   'KW_ESPERAR',
    'REPETIR':   'KW_REPETIR',
    'GUARDAR':   'KW_GUARDAR',
    'EJECUTAR':  'KW_EJECUTAR',
    'IZQUIERDA': 'KW_IZQUIERDA',
    'DERECHA':   'KW_DERECHA',
    'LENTO':     'KW_LENTO',
    'NORMAL':    'KW_NORMAL',
    'RAPIDO':    'KW_RAPIDO',
}

COMANDOS_ANGULO = {'KW_MOVER', 'KW_GIRAR'}


#  CLASIFICADOR DE CARACTERES
def _categoria(ch: str) -> int:
    if 'A' <= ch <= 'Z':  return C_MAY
    if '0' <= ch <= '9':  return C_DIG
    if ch in SEPARADORES: return C_SEP
    return C_ERR


#  CLASE LEXER
class Lexer:
    def __init__(self, codigo: str):
        self.codigo = codigo
        self.pila_errores = PilaErrores()

    def obtener_tokens(self):
        tokens = []
        codigo = self.codigo
        n = len(codigo)

        estado = Q0
        i = 0
        linea = 1
        columna = 1

        buf = []
        buf_lin = 1
        buf_col = 1

        ultimo_kw = None

        while i <= n:

            if i == n:
                if estado in (Q1, Q2, Q3):
                    ultimo_kw = self._emitir_lexema(
                        estado, ''.join(buf), buf_lin, buf_col,
                        tokens, ultimo_kw
                    )
                elif estado == QE:
                    self._error_ilegal(''.join(buf), buf_lin, buf_col)
                break

            ch = codigo[i]
            cat = _categoria(ch)
            sig = TRANS[estado][cat]

            if sig == QF:
                if buf and estado in (Q1, Q2, Q3):
                    ultimo_kw = self._emitir_lexema(
                        estado, ''.join(buf), buf_lin, buf_col,
                        tokens, ultimo_kw
                    )
                    buf = []

                if ch in TOKEN_SEPARADOR:
                    tokens.append((TOKEN_SEPARADOR[ch], ch, linea, columna))

                if ch == '\n':
                    linea += 1
                    columna = 1
                else:
                    columna += 1
                i += 1
                estado = Q0
                continue

            if sig == QE:
                if buf and estado in (Q1, Q2, Q3):
                    ultimo_kw = self._emitir_lexema(
                        estado, ''.join(buf), buf_lin, buf_col,
                        tokens, ultimo_kw
                    )
                    buf = []

                self._error_ilegal(ch, linea, columna)
                columna += 1
                i += 1
                estado = Q0
                continue

            if not buf:
                buf_lin = linea
                buf_col = columna
            buf.append(ch)
            columna += 1
            i += 1
            estado = sig

        return tokens, self.pila_errores

    def _emitir_lexema(self, estado: int, lexema: str, lin: int, col: int,
                       tokens: list, ultimo_kw):

        if estado in (Q1, Q2):
            tipo = PALABRAS_RESERVADAS.get(lexema, 'IDENTIFICADOR')
            tokens.append((tipo, lexema, lin, col))
            return tipo

        elif estado == Q3:
            num = int(lexema)
            if ultimo_kw in COMANDOS_ANGULO:
                if num < 0 or num > 180:
                    self.pila_errores.push(Error(
                        lin, col, lexema,
                        f"Angulo {num} fuera del rango permitido (0-180 grados).",
                        "SEMANTICO",
                        "Use un valor entre 0 y 180 grados"
                    ))
                    return None
            tokens.append(('NUMERO', lexema, lin, col))
            return 'NUMERO'

        return ultimo_kw

    def _error_ilegal(self, ch: str, lin: int, col: int):
        self.pila_errores.push(Error(
            lin, col, ch,
            f"Caracter '{ch}' no pertenece al alfabeto de HAWKE.",
            "LEXICO",
            "Elimine el caracter o revise la instruccion"
        ))