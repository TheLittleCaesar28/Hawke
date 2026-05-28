#  HAWKE - Tabla de Simbolos
#  Almacena rutinas del usuario, estado del brazo y TODOS los símbolos


class TablaSimbolos:
    """
    Tabla de simbolos del interprete HAWKE.
    Almacena:
    1. TODOS los símbolos encontrados (lexemas, tokens, posición)
    2. Rutinas definidas por el usuario
    3. Estado del brazo robotico
    """

    def __init__(self):
        """Inicializa todas las estructuras de la tabla de símbolos."""
        
        # TABLA DE SÍMBOLOS PRINCIPAL (todos los símbolos encontrados)
        self.simbolos = []
        
        # TABLA DE RUTINAS (definidas por el usuario con GUARDAR)
        self.rutinas = {}

        # ESTADO DEL BRAZO (tiempo real durante ejecución)
        self.estado = {
            'pinza':      0,        # 0 = abierto, 180 = cerrado
            'brazo_h':    90,       # angulo horizontal (0-180, 90 = centro)
            'brazo_v':    45,       # angulo vertical   (0-180, 45 = reposo)
            'velocidad':  'NORMAL'  # LENTO | NORMAL | RAPIDO
        }

        # Limites fisicos del brazo
        self.limites = {
            'pinza':   (0, 180),
            'brazo_h': (0, 180),
            'brazo_v': (0, 180),
        }
        
        # CONTEXTO DE CADA TIPO DE TOKEN
        self.palabras_reservadas = {
            'KW_ABRIR', 'KW_CERRAR', 'KW_MOVER', 'KW_GIRAR',
            'KW_ESPERAR', 'KW_REPETIR', 'KW_GUARDAR', 'KW_EJECUTAR',
            'KW_IZQUIERDA', 'KW_DERECHA', 'KW_LENTO', 'KW_NORMAL', 'KW_RAPIDO'
        }

    def agregar_simbolo(self, token_tipo, token_valor, linea, columna):
        """
        Agrega un símbolo a la tabla de símbolos.
        
        Parámetros:
        token_tipo (str): Tipo de token (ej: 'KW_ABRIR', 'NUMERO')
        token_valor (str): Lexema encontrado (ej: 'ABRIR', '90')
        linea (int): Número de línea
        columna (int): Posición en la línea
        """
        # Determinar el contexto del símbolo
        if token_tipo in self.palabras_reservadas:
            contexto = "Palabra Reservada"
        elif token_tipo == 'IDENTIFICADOR':
            contexto = "Identificador"
        elif token_tipo == 'NUMERO':
            contexto = "Número"
        elif token_tipo in ('PUNTO_COMA', 'LLAVE_ABR', 'LLAVE_CER'):
            contexto = "Símbolo"
        else:
            contexto = "Desconocido"
        
        self.simbolos.append({
            'lexema': token_valor,
            'token': token_tipo,
            'linea': linea,
            'columna': columna,
            'contexto': contexto
        })

    def guardar_rutina(self, nombre, instrucciones, linea):
        """
        Guarda una rutina en la tabla de simbolos.
        """
        if nombre in self.rutinas:
            print(f"Advertencia: Sobrescribiendo rutina '{nombre}' "
                  f"(declarada en linea {self.rutinas[nombre]['linea']})")

        self.rutinas[nombre] = {
            'instrucciones': instrucciones,
            'linea':         linea,
            'tipo':          'RUTINA'
        }

    def obtener_rutina(self, nombre):
        """
        Recupera las instrucciones de una rutina guardada.
        """
        if nombre not in self.rutinas:
            return None
        return self.rutinas[nombre]['instrucciones']

    def rutina_existe(self, nombre):
        """Retorna True si la rutina esta definida."""
        return nombre in self.rutinas

    def actualizar_estado(self, componente, valor):
        """
        Actualiza el estado del brazo y valida limites.
        """
        if componente in ('pinza', 'brazo_h', 'brazo_v'):
            minimo, maximo = self.limites[componente]
            if valor < minimo or valor > maximo:
                return False
            self.estado[componente] = valor

        elif componente == 'velocidad':
            if valor not in ('LENTO', 'NORMAL', 'RAPIDO'):
                return False
            self.estado[componente] = valor

        return True

    def mostrar_estado(self):
        """Muestra el estado actual del brazo."""
        print("\n" + "=" * 40)
        print("ESTADO ACTUAL DEL BRAZO")
        print("=" * 40)
        print(f"  Pinza:       {self.estado['pinza']}  ({self._texto_pinza()})")
        print(f"  Horizontal:  {self.estado['brazo_h']}°")
        print(f"  Vertical:    {self.estado['brazo_v']}°")
        print(f"  Velocidad:   {self.estado['velocidad']}")
        print("=" * 40)

    def estado_como_dict(self):
        """Retorna el estado como diccionario (util para la GUI)."""
        return dict(self.estado)

    def _texto_pinza(self):
        v = self.estado['pinza']
        if v == 0:
            return "ABIERTA"
        elif v == 180:
            return "CERRADA"
        return f"PARCIAL ({v})"

    def mostrar_tabla_completa(self):
        """Muestra la tabla de símbolos completa."""
        if not self.simbolos:
            print("\n" + "="*60)
            print("TABLA DE SÍMBOLOS (vacía - no se ha analizado ningún código)")
            print("="*60)
            return
        
        print("\n" + "="*80)
        print("TABLA DE SÍMBOLOS - TODOS LOS SÍMBOLOS ENCONTRADOS")
        print("="*80)
        print(f"{'Lexema':<20} {'Token':<20} {'Línea':<8} {'Columna':<10} {'Contexto'}")
        print("-"*80)
        
        for s in self.simbolos:
            lexema = s['lexema'][:18] if len(s['lexema']) > 18 else s['lexema']
            token = s['token'][:18] if len(s['token']) > 18 else s['token']
            print(f"{lexema:<20} {token:<20} {s['linea']:<8} {s['columna']:<10} {s['contexto']}")
        
        print("="*80)
        print(f"Total de símbolos: {len(self.simbolos)}")

    def listar_rutinas(self):
        """Muestra todas las rutinas guardadas."""
        if not self.rutinas:
            print("  No hay rutinas guardadas.")
            return
        print("\n" + "=" * 40)
        print("RUTINAS GUARDADAS")
        print("=" * 40)
        for nombre, info in self.rutinas.items():
            n = len(info['instrucciones'])
            print(f"  {nombre}: {n} instrucciones (linea {info['linea']})")
    
    def limpiar_simbolos(self):
        """Limpia la tabla de símbolos (para una nueva ejecución)."""
        self.simbolos = []
        self.rutinas = {}