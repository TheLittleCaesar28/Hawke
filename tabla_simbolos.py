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
        
        #  todos los símbolos encontrados
        # Lista de símbolos: cada uno es un diccionario con:
        #   - lexema: texto encontrado
        #   - token: tipo de token
        #   - linea: número de línea
        #   - columna: posición en la línea
        #   - contexto: 'Palabra Reservada', 'Identificador', 'Número', 'Símbolo'
        self.simbolos = []
        
        #  TABLA DE RUTINAS (definidas por el usuario con GUARDAR)
        # nombre -> {instrucciones, linea, tipo}
        self.rutinas = {}

        #  ESTADO DEL BRAZO (tiempo real durante ejecución)
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
        
        #  CONTEXTO DE CADA TIPO DE TOKEN
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

        Parametros:
        nombre (str): Nombre de la rutina
        instrucciones (list): Lista de instrucciones que contiene
        linea (int): Numero de linea donde se declaro
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

        Retorna:
        list | None: instrucciones o None si no existe
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

        Retorna:
        bool: True si fue valido, False si excede limites
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
        """
        MUESTRA LA TABLA DE SÍMBOLOS COMPLETA:
        - Todos los lexemas encontrados
        - Su tipo de token
        - Línea y columna
        - Contexto
        """
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

    def mostrar_tabla_rutinas(self):
        """
        MUESTRA LA TABLA DE RUTINAS GUARDADAS.
        """
        if not self.rutinas:
            print("\n" + "="*50)
            print("TABLA DE RUTINAS (vacía)")
            print("="*50)
            return
        
        print("\n" + "="*70)
        print("TABLA DE RUTINAS - GUARDADAS CON 'GUARDAR'")
        print("="*70)
        print(f"{'Nombre':<15} {'Tipo':<10} {'Línea':<8} {'Instrucciones'}")
        print("-"*70)
        
        for nombre, info in self.rutinas.items():
            nombre_str = nombre[:14] if len(nombre) > 14 else nombre
            tipo = info.get('tipo', 'RUTINA')
            linea = info['linea']
            num_inst = len(info['instrucciones'])
            print(f"{nombre_str:<15} {tipo:<10} {linea:<8} {num_inst} instrucción(es)")
        
        print("="*70)

    def listar_rutinas(self):
        """Muestra todas las rutinas guardadas (formato simple)."""
        if not self.rutinas:
            print("  No hay rutinas guardadas.")
            return
        print("\n" + "=" * 40)
        print("RUTINAS GUARDADAS")
        print("=" * 40)
        for nombre, info in self.rutinas.items():
            n = len(info['instrucciones'])
            print(f"  {nombre}: {n} instrucciones (linea {info['linea']})")
        print("=" * 40)
    
    def limpiar_simbolos(self):
        """Limpia la tabla de símbolos (para una nueva ejecución)."""
        self.simbolos = []
        self.rutinas = {}


#  PRUEBA DE LA TABLA DE SÍMBOLOS

if __name__ == "__main__":
    print("="*60)
    print("PRUEBA DE LA TABLA DE SÍMBOLOS COMPLETA")
    print("="*60)
    
    # Crear tabla de símbolos
    tabla = TablaSimbolos()
    
    # Agregar símbolos de ejemplo
    tabla.agregar_simbolo('KW_ABRIR', 'ABRIR', 1, 1)
    tabla.agregar_simbolo('PUNTO_COMA', ';', 1, 6)
    tabla.agregar_simbolo('KW_MOVER', 'MOVER', 2, 1)
    tabla.agregar_simbolo('NUMERO', '90', 2, 7)
    tabla.agregar_simbolo('KW_RAPIDO', 'RAPIDO', 2, 10)
    tabla.agregar_simbolo('PUNTO_COMA', ';', 2, 16)
    tabla.agregar_simbolo('IDENTIFICADOR', 'AGARRAR', 3, 9)
    tabla.agregar_simbolo('LLAVE_ABR', '{', 3, 16)
    
    # Mostrar tabla completa
    tabla.mostrar_tabla_completa()
    
    # Agregar rutinas de ejemplo
    tabla.guardar_rutina("AGARRAR", [
        ('MOVER', 30, 'LENTO'),
        ('CERRAR',),
        ('ESPERAR', 500)
    ], 5)
    
    # Mostrar tabla de rutinas
    tabla.mostrar_tabla_rutinas()