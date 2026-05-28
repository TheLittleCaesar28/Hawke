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
        self.simbolos = []      # Todos los símbolos encontrados
        self.rutinas = {}       # Rutinas: nombre -> instrucciones
        self.estado = {
            'pinza': 0,
            'brazo_h': 90,
            'brazo_v': 45,
            'velocidad': 'NORMAL'
        }
        self.limites = {
            'pinza': (0, 180),
            'brazo_h': (0, 180),
            'brazo_v': (0, 180),
        }
        self.palabras_reservadas = {
            'KW_ABRIR', 'KW_CERRAR', 'KW_MOVER', 'KW_GIRAR',
            'KW_ESPERAR', 'KW_REPETIR', 'KW_GUARDAR', 'KW_EJECUTAR',
            'KW_IZQUIERDA', 'KW_DERECHA', 'KW_LENTO', 'KW_NORMAL', 'KW_RAPIDO'
        }

    def agregar_simbolo(self, token_tipo, token_valor, linea, columna):
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
        if nombre in self.rutinas:
            print(f"Advertencia: Sobrescribiendo rutina '{nombre}'")
        self.rutinas[nombre] = {
            'instrucciones': instrucciones,
            'linea': linea,
            'tipo': 'RUTINA'
        }

    def obtener_rutina(self, nombre):
        if nombre not in self.rutinas:
            return None
        return self.rutinas[nombre]['instrucciones']

    def rutina_existe(self, nombre):
        return nombre in self.rutinas

    def actualizar_estado(self, componente, valor):
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
        print("\n" + "=" * 40)
        print("ESTADO ACTUAL DEL BRAZO")
        print("=" * 40)
        print(f"  Pinza:       {self.estado['pinza']}°")
        print(f"  Horizontal:  {self.estado['brazo_h']}°")
        print(f"  Vertical:    {self.estado['brazo_v']}°")
        print(f"  Velocidad:   {self.estado['velocidad']}")
        print("=" * 40)

    def estado_como_dict(self):
        return dict(self.estado)

    def limpiar_simbolos(self):
        self.simbolos = []
        self.rutinas = {}