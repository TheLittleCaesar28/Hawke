#HAWKE - Analizador Léxico con Autómata Finito Determinista (AFD)
#  Matriz de transición
# ESTADOS                                                                                                    
# Q0  -> inicial                                                  
# Q1  ->leyendo letras A-Z (solo mayúsculas desde q0)           
# Q2  ->leyendo mezcla letra|dígito (una vez que Q1 vio algo)   
# Q3  -> leyendo dígitos (desde q0, solo dígitos)                
# QF  -> estado final aceptor (llegamos por separador)           
# QE  ->estado error (minúscula, @, #, etc.)                    

#  
#  CATEGORÍAS DE CARACTERES  (columnas de la matriz)             
#                                                                  
#  C_MAY  → A-Z                                                  
#  C_DIG  → 0-9                                                 
#  C_SEP  → espacio, tab, \n, ;, {, }   ← separadores del AFD   
#  C_ERR  → cualquier otro (minúscula, @, #, …)                  
#  
#
#  MATRIZ  TRANS[estado][categoria]:
#
#           C_MAY  C_DIG  C_SEP  C_ERR
#  ─────────────────────────────────────
#  Q0    │   Q1     Q3     QF     QE
#  Q1    │   Q1     Q2     QF     QE
#  Q2    │   Q2     Q2     QF     QE
#  Q3    │   QE     Q3     QF     QE
#  QF    │   —      —      —      —     (aceptor: se emite y vuelve a Q0)
#  QE    │   —      —      —      —     (error: se reporta y vuelve a Q0)

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


#  SEPARADORES  (los que disparan QF según el diagrama)
#  espacio · tab · \n · ; · { · }
SEPARADORES = {' ', '\t', '\n', ';', '{', '}'}

# Tokens que emite cada separador de un solo carácter
TOKEN_SEPARADOR = {
    ';': 'PUNTO_COMA',
    '{': 'LLAVE_ABR',
    '}': 'LLAVE_CER',
}


#  MATRIZ DE TRANSICIÓN   TRANS[estado][categoria] → sig. estado
#  Columnas:  0=C_MAY  1=C_DIG  2=C_SEP  3=C_ERR

TRANS = [
    #      MAY  DIG  SEP  ERR
    # Q0
    [       Q1,  Q3,  QF,  QE ],
    # Q1  — letras desde q0: letra → Q1, dígito → Q2, sep → QF, otro → QE
    [       Q1,  Q2,  QF,  QE ],
    # Q2  — mezcla letra|dígito: ambos extienden Q2, sep → QF, otro → QE
    [       Q2,  Q2,  QF,  QE ],
    # Q3  — solo dígitos: dígito → Q3, sep → QF, letra/otro → QE
    [       QE,  Q3,  QF,  QE ],
    # QF  — aceptor (nunca se consulta; la lógica lo maneja aparte)
    [       Q0,  Q0,  Q0,  Q0 ],
    # QE  — error   (ídem)
    [       Q0,  Q0,  Q0,  Q0 ],
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

# Comandos cuyo siguiente NUMERO debe ser ángulo (0-180)
COMANDOS_ANGULO = {'KW_MOVER', 'KW_GIRAR'}


#  CLASIFICADOR DE CARACTERES
def _categoria(ch: str) -> int:
    """Devuelve el índice de categoría para un carácter dado."""
    if 'A' <= ch <= 'Z':  return C_MAY
    if '0' <= ch <= '9':  return C_DIG
    if ch in SEPARADORES: return C_SEP
    return C_ERR


#  CLASE LEXER
class Lexer:
    """
    Analizador léxico para HAWKE.
    La MATRIZ DE TRANSICIÓN corresponde exactamente al AFD del diagrama
    (estados q0, q1, q2, q3, qF, ERROR; separadores: espacio, tab, \\n, ;, {, }).
    No usa re ni ninguna librería externa.
    """

    def __init__(self, codigo: str):
        self.codigo       = codigo
        self.pila_errores = PilaErrores()

    #  Método principal
    def obtener_tokens(self):
        """
        Recorre el código carácter a carácter guiado por TRANS[][].

        Retorna:
            (list[tuple], PilaErrores)
            Cada token: (tipo, valor, linea, columna)
        """
        tokens    = []
        codigo    = self.codigo
        n         = len(codigo)

        estado    = Q0
        i         = 0
        linea     = 1
        columna   = 1

        # Buffer del lexema en construcción
        buf       = []
        buf_lin   = 1
        buf_col   = 1

        # Rastrea el último tipo de token emitido para validar ángulos
        ultimo_kw = None

        while i <= n:

            # ── Fin de entrada 
            if i == n:
                if estado in (Q1, Q2, Q3):
                    ultimo_kw = self._emitir_lexema(
                        estado, ''.join(buf), buf_lin, buf_col,
                        tokens, ultimo_kw
                    )
                elif estado == QE:
                    self._error_ilegal(''.join(buf), buf_lin, buf_col)
                break

            ch  = codigo[i]
            
            # ═══════════════════════════════════════════════════════════════
            #  DETECTAR COMENTARIOS // (ignorar toda la línea)
            #  Esto se hace ANTES del autómata para que los comentarios
            #  no generen errores ni afecten el estado del autómata.
            # ═══════════════════════════════════════════════════════════════
            if ch == '/' and i + 1 < n and codigo[i + 1] == '/':
                # Saltar todo hasta el final de la línea
                while i < n and codigo[i] != '\n':
                    i += 1
                    columna += 1
                # Saltar el '\n' si existe
                if i < n and codigo[i] == '\n':
                    i += 1
                    linea += 1
                    columna = 1
                continue  # Volver al inicio del bucle
            
            # ═══════════════════════════════════════════════════════════════
            #  FIN DETECCIÓN DE COMENTARIOS
            # ═══════════════════════════════════════════════════════════════
            
            cat = _categoria(ch)
            sig = TRANS[estado][cat]

            #  LLEGAMOS A QF (separador)
            if sig == QF:
                # Emitir lexema pendiente
                if buf and estado in (Q1, Q2, Q3):
                    ultimo_kw = self._emitir_lexema(
                        estado, ''.join(buf), buf_lin, buf_col,
                        tokens, ultimo_kw
                    )
                    buf = []

                # Emitir token del separador (;, {, })
                if ch in TOKEN_SEPARADOR:
                    tokens.append((TOKEN_SEPARADOR[ch], ch, linea, columna))

                # Actualizar posición
                if ch == '\n':
                    linea   += 1
                    columna  = 1
                else:
                    columna += 1
                i      += 1
                estado  = Q0
                continue

            #  LLEGAMOS A QE (error)
            if sig == QE:
                # Emitir lexema pendiente si había
                if buf and estado in (Q1, Q2, Q3):
                    ultimo_kw = self._emitir_lexema(
                        estado, ''.join(buf), buf_lin, buf_col,
                        tokens, ultimo_kw
                    )
                    buf = []

                # Reportar el carácter ilegal
                self._error_ilegal(ch, linea, columna)
                columna += 1
                i       += 1
                estado   = Q0
                continue

            #  TRANSICIÓN NORMAL
            if not buf:
                buf_lin = linea
                buf_col = columna
            buf.append(ch)
            columna += 1
            i       += 1
            estado   = sig

        return tokens, self.pila_errores

    #  Emisión de lexema según estado aceptor
    def _emitir_lexema(self, estado: int, lexema: str, lin: int, col: int,
                       tokens: list, ultimo_kw):
        """
        Clasifica el lexema acumulado en Q1/Q2/Q3, aplica validaciones
        semánticas y agrega a tokens o a la pila de errores.

        Retorna el tipo del token emitido (para rastrear ángulos).
        """

        # Q1 o Q2: letras (con posibles dígitos) → KW o IDENTIFICADOR
        if estado in (Q1, Q2):
            tipo = PALABRAS_RESERVADAS.get(lexema, 'IDENTIFICADOR')
            tokens.append((tipo, lexema, lin, col))
            return tipo

        # Q3: dígitos → NUMERO (+ validación de ángulo)
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

    #
    def _error_ilegal(self, ch: str, lin: int, col: int):
        self.pila_errores.push(Error(
            lin, col, ch,
            f"Caracter '{ch}' no pertenece al alfabeto de HAWKE.",
            "LEXICO",
            "Elimine el caracter o revise la instruccion"
        ))