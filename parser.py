#  HAWKE - Analizador Sintactico (Parser)
#  Verifica que los tokens sigan la gramatica BNF del lenguaje

from pila_errores import PilaErrores, Error
from tabla_simbolos import TablaSimbolos


class Parser:
    """
    Analizador sintactico para HAWKE.
    Verifica que los tokens sigan la gramatica BNF del lenguaje.
    """

    def __init__(self, tokens):
        """
        Inicializa el parser con una lista de tokens.

        Parametros:
        tokens: Lista de tuplas (tipo, valor, linea, columna)
        """
        self.tokens       = tokens
        self.pos          = 0
        self.pila_errores = PilaErrores()
        self.tabla_sim    = TablaSimbolos()

    # ── Utilidades ────────────────────────────────────────────────────────

    def token_actual(self):
        """Retorna el token en la posicion actual, o None si no hay mas."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consumir(self, tipo_esperado):
        """
        Consume el token actual si coincide con el tipo esperado.
        Si no coincide, registra un error y retorna None.
        """
        token = self.token_actual()
        if token and token[0] == tipo_esperado:
            self.pos += 1
            return token

        # Error sintactico
        if token:
            lin, col, actual = token[2], token[3], token[0]
        else:
            ultimo = self.tokens[-1] if self.tokens else None
            lin    = ultimo[2] if ultimo else 0
            col    = ultimo[3] if ultimo else 0
            actual = "FIN_DE_ARCHIVO"

        self.pila_errores.push(Error(
            lin, col, actual,
            f"Se esperaba '{tipo_esperado}', se encontro '{actual}'",
            "SINTACTICO",
            f"Revise la sintaxis del comando"
        ))
        return None

    def sincronizar(self):
        """
        Modo panic: avanza hasta el proximo ';' o '}' para seguir analizando.
        """
        while self.pos < len(self.tokens):
            if self.tokens[self.pos][0] in ('PUNTO_COMA', 'LLAVE_CER'):
                self.pos += 1
                break
            self.pos += 1

    # ── Punto de entrada ──────────────────────────────────────────────────

    def parse(self):
        """
        Analiza toda la secuencia de tokens.
        Retorna: (lista_de_instrucciones, pila_de_errores)
        """
        instrucciones = []
        
        # Limpiar tabla de símbolos antes de nuevo análisis
        self.tabla_sim.limpiar_simbolos()

        while self.pos < len(self.tokens):
            # Agregar el token actual a la tabla de símbolos
            token = self.token_actual()
            if token:
                self.tabla_sim.agregar_simbolo(token[0], token[1], token[2], token[3])
            
            instruccion = self.parse_instruccion()
            if instruccion:
                instrucciones.append(instruccion)
                self.consumir('PUNTO_COMA')
            else:
                self.sincronizar()

        return instrucciones, self.pila_errores

    # ── Despacho de instrucciones ─────────────────────────────────────────

    def parse_instruccion(self):
        """
        Gramatica:
        <instruccion> ::= ABRIR | CERRAR | MOVER | GIRAR
                        | ESPERAR | REPETIR | GUARDAR | EJECUTAR
        """
        token = self.token_actual()
        if not token:
            return None

        dispatch = {
            'KW_ABRIR':    self.parse_abrir,
            'KW_CERRAR':   self.parse_cerrar,
            'KW_MOVER':    self.parse_mover,
            'KW_GIRAR':    self.parse_girar,
            'KW_ESPERAR':  self.parse_esperar,
            'KW_REPETIR':  self.parse_repetir,
            'KW_GUARDAR':  self.parse_guardar,
            'KW_EJECUTAR': self.parse_ejecutar,
        }

        handler = dispatch.get(token[0])
        if handler:
            return handler()

        # Token no reconocido como instruccion
        self.pila_errores.push(Error(
            token[2], token[3], token[1],
            f"Instruccion no reconocida: '{token[1]}'",
            "SINTACTICO",
            "Verifique que el comando exista en el lenguaje HAWKE"
        ))
        self.pos += 1
        return None

    # ── Instrucciones simples ─────────────────────────────────────────────

    def parse_abrir(self):
        """ABRIR;"""
        tok = self.consumir('KW_ABRIR')
        if not tok:
            return None
        return ('ABRIR',)

    def parse_cerrar(self):
        """CERRAR;"""
        tok = self.consumir('KW_CERRAR')
        if not tok:
            return None
        return ('CERRAR',)

    def parse_mover(self):
        """
        MOVER NUMERO [LENTO|NORMAL|RAPIDO];
        Ejemplo: MOVER 90 LENTO;
        """
        self.consumir('KW_MOVER')

        token_num = self.consumir('NUMERO')
        if not token_num:
            return None
        angulo = int(token_num[1])

        # Velocidad opcional
        velocidad = 'NORMAL'
        tok = self.token_actual()
        if tok and tok[0] in ('KW_LENTO', 'KW_NORMAL', 'KW_RAPIDO'):
            velocidad = tok[1]
            self.pos += 1

        return ('MOVER', angulo, velocidad)

    def parse_girar(self):
        """
        GIRAR (IZQUIERDA|DERECHA) NUMERO [LENTO|NORMAL|RAPIDO];
        Ejemplo: GIRAR DERECHA 90;
        """
        self.consumir('KW_GIRAR')

        tok_dir = self.token_actual()
        if not tok_dir or tok_dir[0] not in ('KW_IZQUIERDA', 'KW_DERECHA'):
            lin = tok_dir[2] if tok_dir else 0
            col = tok_dir[3] if tok_dir else 0
            val = tok_dir[1] if tok_dir else "?"
            self.pila_errores.push(Error(
                lin, col, val,
                f"Se esperaba IZQUIERDA o DERECHA, se encontro '{val}'",
                "SINTACTICO",
                "Use: GIRAR IZQUIERDA <angulo> o GIRAR DERECHA <angulo>"
            ))
            return None

        direccion = tok_dir[1]
        self.pos += 1

        tok_ang = self.consumir('NUMERO')
        if not tok_ang:
            return None
        angulo = int(tok_ang[1])

        # Velocidad opcional
        velocidad = 'NORMAL'
        tok = self.token_actual()
        if tok and tok[0] in ('KW_LENTO', 'KW_NORMAL', 'KW_RAPIDO'):
            velocidad = tok[1]
            self.pos += 1

        return ('GIRAR', direccion, angulo, velocidad)

    def parse_esperar(self):
        """
        ESPERAR NUMERO;
        Ejemplo: ESPERAR 500;
        """
        self.consumir('KW_ESPERAR')
        tok = self.consumir('NUMERO')
        if not tok:
            return None
        return ('ESPERAR', int(tok[1]))

    def parse_ejecutar(self):
        """
        EJECUTAR IDENTIFICADOR;
        Ejemplo: EJECUTAR SALUDO;
        """
        self.consumir('KW_EJECUTAR')
        tok = self.token_actual()

        if not tok or tok[0] != 'IDENTIFICADOR':
            lin = tok[2] if tok else 0
            col = tok[3] if tok else 0
            val = tok[1] if tok else "?"
            self.pila_errores.push(Error(
                lin, col, val,
                f"Se esperaba nombre de rutina, se encontro '{val}'",
                "SINTACTICO",
                "Use: EJECUTAR NOMBRE_RUTINA"
            ))
            return None

        nombre = tok[1]
        self.pos += 1

        # Validacion semantica: la rutina debe estar declarada
        if not self.tabla_sim.rutina_existe(nombre):
            self.pila_errores.push(Error(
                tok[2], tok[3], nombre,
                f"La rutina '{nombre}' no esta declarada",
                "SEMANTICO",
                f"Declare la rutina con: GUARDAR {nombre} {{ ... }}"
            ))

        return ('EJECUTAR', nombre)

    # ── Instrucciones con bloque ──────────────────────────────────────────

    def parse_repetir(self):
        """
        REPETIR NUMERO { <instruccion>* }
        Ejemplo: REPETIR 3 { MOVER 90; }
        """
        self.consumir('KW_REPETIR')

        tok_num = self.consumir('NUMERO')
        if not tok_num:
            return None
        repeticiones = int(tok_num[1])

        if repeticiones <= 0:
            self.pila_errores.push(Error(
                tok_num[2], tok_num[3], tok_num[1],
                "El numero de repeticiones debe ser mayor que 0",
                "SEMANTICO",
                "Use REPETIR 1, REPETIR 2, etc."
            ))

        if not self.consumir('LLAVE_ABR'):
            return None

        instrucciones_bloque = self._parsear_bloque()

        if not self.consumir('LLAVE_CER'):
            return None

        return ('REPETIR', repeticiones, instrucciones_bloque)

    def parse_guardar(self):
        """
        GUARDAR IDENTIFICADOR { <instruccion>* }
        Ejemplo: GUARDAR SALUDO { ABRIR; MOVER 90; }
        """
        tok_kw = self.consumir('KW_GUARDAR')
        if not tok_kw:
            return None

        # Nombre de la rutina — debe ser IDENTIFICADOR
        tok_id = self.token_actual()
        if not tok_id or tok_id[0] != 'IDENTIFICADOR':
            lin = tok_id[2] if tok_id else tok_kw[2]
            col = tok_id[3] if tok_id else tok_kw[3]
            val = tok_id[1] if tok_id else "?"
            self.pila_errores.push(Error(
                lin, col, val,
                f"Se esperaba nombre de rutina, se encontro '{val}'",
                "SINTACTICO",
                "Use: GUARDAR NOMBRE_RUTINA { ... }"
            ))
            return None

        nombre  = tok_id[1]
        linea   = tok_id[2]
        self.pos += 1

        if not self.consumir('LLAVE_ABR'):
            return None

        instrucciones_rutina = self._parsear_bloque()

        if not self.consumir('LLAVE_CER'):
            return None

        # Registrar en tabla de simbolos
        self.tabla_sim.guardar_rutina(nombre, instrucciones_rutina, linea)

        return ('GUARDAR', nombre, instrucciones_rutina)

    # ── Auxiliar para parsear bloques { } 

    def _parsear_bloque(self):
        """Parsea instrucciones hasta encontrar una llave de cierre."""
        instrucciones = []
        while self.token_actual() and self.token_actual()[0] != 'LLAVE_CER':
            inst = self.parse_instruccion()
            if inst:
                instrucciones.append(inst)
            if self.token_actual() and self.token_actual()[0] == 'PUNTO_COMA':
                self.consumir('PUNTO_COMA')
        return instrucciones