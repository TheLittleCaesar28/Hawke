# HAWKE - Analizador Léxico con Autómata Finito Determinista (AFD)
#  Matriz de transición

# ESTADOS:                                                        
# Q0  -> inicial                                                  
# Q1  -> leyendo letras A-Z (solo mayúsculas desde q0)           
# Q2  -> leyendo mezcla letra|dígito (una vez que Q1 vio algo)   
# Q3  -> leyendo dígitos (desde q0, solo dígitos)                
# QF  -> estado final aceptor (llegamos por separador)           
# QE  -> estado error (minúscula, @, #, etc.)                    

# MATRIZ DE TRANSICIÓN:
#           C_MAY  C_DIG  C_SEP  C_ERR
#  ─────────────────────────────────────
#  Q0    │   Q1     Q3     QF     QE
#  Q1    │   Q1     Q2     QF     QE
#  Q2    │   Q2     Q2     QF     QE
#  Q3    │   QE     Q3     QF     QE
#  QF    │   Q0     Q0     Q0     Q0
#  QE    │   Q0     Q0     Q0     Q0

from pila_errores import PilaErrores, Error


#  ÍNDICES DE CATEGORÍAS (columnas)
C_MAY = 0   # A-Z
C_DIG = 1   # 0-9
C_SEP = 2   # espacio, tab, \n, ;, {, }
C_ERR = 3   # cualquier otro carácter (minúsculas, @, #, etc.)


#  ÍNDICES DE ESTADOS (filas)
Q0 = 0   # inicial
Q1 = 1   # leyendo letras A-Z
Q2 = 2   # leyendo mezcla letra|dígito
Q3 = 3   # leyendo dígitos
QF = 4   # final / aceptor
QE = 5   # error


#  SEPARADORES
SEPARADORES = {' ', '\t', '\n', ';', '{', '}'}

TOKEN_SEPARADOR = {
    ';': 'PUNTO_COMA',
    '{': 'LLAVE_ABR',
    '}': 'LLAVE_CER',
}


#  MATRIZ DE TRANSICIÓN
TRANS = [
    #      MAY  DIG  SEP  ERR
    [       Q1,  Q3,  QF,  QE ],  # Q0
    [       Q1,  Q2,  QF,  QE ],  # Q1
    [       Q2,  Q2,  QF,  QE ],  # Q2
    [       QE,  Q3,  QF,  QE ],  # Q3
    [       Q0,  Q0,  Q0,  Q0 ],  # QF (reinicia)
    [       Q0,  Q0,  Q0,  Q0 ],  # QE (reinicia)
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
    if 'A' <= ch <= 'Z':
        return C_MAY
    if '0' <= ch <= '9':
        return C_DIG
    if ch in SEPARADORES:
        return C_SEP
    return C_ERR


#  CLASE LEXER
class Lexer:
    """
    Analizador léxico para HAWKE.
    Implementa un AFD con matriz de transición.
    No usa re ni ninguna librería externa.
    """

    def __init__(self, codigo: str):
        self.codigo = codigo
        self.pila_errores = PilaErrores()

    #  Método principal
    def obtener_tokens(self):
        """
        Recorre el código carácter a carácter guiado por la matriz de transición.

        Retorna:
            (list[tuple], PilaErrores)
            Cada token: (tipo, valor, linea, columna)
        """
        tokens = []
        codigo = self.codigo
        n = len(codigo)

        estado = Q0
        i = 0
        linea = 1
        columna = 1

        # Buffer para construir el lexema
        buf = []
        buf_lin = 1
        buf_col = 1

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

            ch = codigo[i]
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
                    linea += 1
                    columna = 1
                else:
                    columna += 1
                i += 1
                estado = Q0
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
                i += 1
                estado = Q0
                continue

            
            #  TRANSICIÓN NORMAL
            if not buf:
                buf_lin = linea
                buf_col = columna
            buf.append(ch)
            columna += 1
            i += 1
            estado = sig

        return tokens, self.pila_errores

    #  Emisión de lexema según estado
    def _emitir_lexema(self, estado: int, lexema: str, lin: int, col: int,
                       tokens: list, ultimo_kw):
        """
        Clasifica el lexema acumulado y lo agrega a tokens.
        """

        # Q1 o Q2: palabra (reservada o identificador)
        if estado in (Q1, Q2):
            tipo = PALABRAS_RESERVADAS.get(lexema, 'IDENTIFICADOR')
            tokens.append((tipo, lexema, lin, col))
            return tipo

        # Q3: número
        elif estado == Q3:
            num = int(lexema)
            # Validar ángulo si viene después de MOVER o GIRAR
            if ultimo_kw in COMANDOS_ANGULO:
                if num < 0 or num > 180:
                    self.pila_errores.push(Error(
                        lin, col, lexema,
                        f"Angulo {num} fuera del rango permitido (0-180 grados).",
                        "SEMANTICO (M01)",
                        "Use un valor entre 0 y 180 grados"
                    ))
                    return None
            tokens.append(('NUMERO', lexema, lin, col))
            return 'NUMERO'

        return ultimo_kw


    def _error_ilegal(self, ch: str, lin: int, col: int):
        """Registra un error por carácter ilegal."""
        self.pila_errores.push(Error(
            lin, col, ch,
            f"Caracter '{ch}' no pertenece al alfabeto de HAWKE.",
            "LEXICO (E001)",
            "Elimine el caracter o revise la instruccion"
        ))


#  PRUEBA DEL LEXER (ejecutar directamente)
if __name__ == "__main__":
    print("="*60)
    print("PRUEBA DEL LEXER")
    print("="*60)
    
    # Código de prueba
    codigo_prueba = """
ABRIR;
MOVER 90 RAPIDO;
GUARDAR TEST {
    CERRAR;
};
EJECUTAR TEST;
"""
    
    print(f"\nCÓDIGO A ANALIZAR:\n{codigo_prueba}")
    
    # Crear lexer
    lexer = Lexer(codigo_prueba)
    
    # Obtener tokens
    tokens, errores = lexer.obtener_tokens()
    
    print("\n" + "="*60)
    print("TOKENS GENERADOS")
    print("="*60)
    for token in tokens:
        print(f"  {token}")
    
    if errores.hay_errores():
        print("\n" + "="*60)
        print("ERRORES ENCONTRADOS")
        print("="*60)
        errores.mostrar_todos()
    else:
        print("\n No se encontraron errores")
        print("\n LEXER FUNCIONANDO CORRECTAMENTE")