#  HAWKE - Tabla de Simbolos
#  Almacena rutinas del usuario y estado del brazo robotico


class TablaSimbolos:
    """
    Tabla de simbolos del interprete HAWKE.
    Almacena rutinas definidas por el usuario y el estado del brazo.
    """

    def __init__(self):
        """Inicializa la tabla de rutinas vacia y el estado por defecto del brazo."""
        self.rutinas = {}   # nombre -> {instrucciones, linea, tipo}

        # Estado actual del brazo robotico
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



#  PRUEBA DE LA TABLA DE SÍMBOLOS
if __name__ == "__main__":
    print("="*60)
    print("PRUEBA DE LA TABLA DE SÍMBOLOS")
    print("="*60)
    
    # Crear tabla de símbolos
    tabla = TablaSimbolos()
    
    # Mostrar estado inicial
    tabla.mostrar_estado()
    
    # Guardar rutinas de ejemplo
    print("\n>>> Guardando rutina 'AGARRAR'...")
    tabla.guardar_rutina("AGARRAR", [
        ('MOVER', 30, 'LENTO'),
        ('CERRAR',),
        ('ESPERAR', 500),
        ('MOVER', 90, 'RAPIDO')
    ], 3)
    
    print("\n>>> Guardando rutina 'SOLTAR'...")
    tabla.guardar_rutina("SOLTAR", [
        ('MOVER', 30, 'LENTO'),
        ('ABRIR',),
        ('ESPERAR', 300),
        ('MOVER', 0,)
    ], 8)
    
    # Listar rutinas guardadas
    tabla.listar_rutinas()
    
    # Probar obtener rutina
    print("\n>>> Obteniendo rutina 'AGARRAR':")
    rutina = tabla.obtener_rutina("AGARRAR")
    if rutina:
        print(f"  Instrucciones: {rutina}")
    
    # Probar actualizar estado
    print("\n>>> Actualizando estado del brazo...")
    tabla.actualizar_estado('pinza', 180)
    tabla.actualizar_estado('brazo_v', 90)
    tabla.actualizar_estado('velocidad', 'RAPIDO')
    
    # Mostrar estado actualizado
    tabla.mostrar_estado()
    
    print("\n TABLA DE SÍMBOLOS FUNCIONANDO CORRECTAMENTE")