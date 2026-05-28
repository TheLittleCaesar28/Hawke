# analizador_semantico.py
# Análisis semántico para HAWKE
# Verifica que el programa tenga sentido lógico

from pila_errores import Error


class AnalizadorSemantico:
    """
    Analizador semántico para HAWKE.
    
    Valida:
    - Ángulos entre 0 y 180 grados (M01)
    - Direcciones válidas (IZQUIERDA/DERECHA) (M03)
    - Velocidades válidas (LENTO/NORMAL/RAPIDO) (M04)
    - Repeticiones positivas (M05)
    - Rutinas declaradas antes de ejecutar (M02)
    - Tiempos de espera positivos
    """

    def __init__(self, pila_errores):
        """
        Inicializa el analizador semántico.
        
        Parámetros:
        pila_errores: Instancia de PilaErrores para almacenar errores semánticos
        """
        self.pila_errores = pila_errores
        self.rutinas_declaradas = set()  # Nombres de rutinas definidas

    def validar_programa(self, instrucciones):
        """
        Valida semánticamente todas las instrucciones del programa.
        
        Retorna:
        bool: True si todas son válidas, False si hay errores.
        """
        errores = False
        self.rutinas_declaradas.clear()
        
        for inst in instrucciones:
            if not self.validar_instruccion(inst):
                errores = True
        
        return not errores

    def validar_instruccion(self, instruccion):
        """Valida una instrucción individual según su tipo."""
        cmd = instruccion[0]
        
        if cmd == 'ABRIR':
            return True  # Siempre válido
        elif cmd == 'CERRAR':
            return True  # Siempre válido
        elif cmd == 'MOVER':
            return self._validar_mover(instruccion)
        elif cmd == 'GIRAR':
            return self._validar_girar(instruccion)
        elif cmd == 'ESPERAR':
            return self._validar_esperar(instruccion)
        elif cmd == 'REPETIR':
            return self._validar_repetir(instruccion)
        elif cmd == 'GUARDAR':
            return self._validar_guardar(instruccion)
        elif cmd == 'EJECUTAR':
            return self._validar_ejecutar(instruccion)
        
        return True

    # ============================================================
    # VALIDACIONES ESPECÍFICAS
    # ============================================================

    def _validar_mover(self, inst):
        """Valida MOVER: ángulo (0-180) y velocidad válida."""
        _, angulo, velocidad = inst
        
        # Validar ángulo (M01)
        if angulo < 0 or angulo > 180:
            self.pila_errores.push(Error(
                0, 0, str(angulo),
                f"Ángulo {angulo} fuera del rango permitido (0-180 grados).",
                "SEMÁNTICO (M01)",
                "Use un valor entre 0 y 180 grados"
            ))
            return False
        
        # Validar velocidad (M04)
        if velocidad not in ['LENTO', 'NORMAL', 'RAPIDO']:
            self.pila_errores.push(Error(
                0, 0, velocidad,
                f"Velocidad '{velocidad}' no reconocida.",
                "SEMÁNTICO (M04)",
                "Use LENTO, NORMAL o RAPIDO"
            ))
            return False
        
        return True

    def _validar_girar(self, inst):
        """Valida GIRAR: dirección, ángulo y velocidad."""
        _, direccion, angulo, velocidad = inst
        
        # Validar dirección (M03)
        if direccion not in ['IZQUIERDA', 'DERECHA']:
            self.pila_errores.push(Error(
                0, 0, direccion,
                f"Dirección '{direccion}' inválida.",
                "SEMÁNTICO (M03)",
                "Use IZQUIERDA o DERECHA"
            ))
            return False
        
        # Validar ángulo (M01)
        if angulo < 0 or angulo > 180:
            self.pila_errores.push(Error(
                0, 0, str(angulo),
                f"Ángulo {angulo} fuera del rango permitido (0-180 grados).",
                "SEMÁNTICO (M01)",
                "Use un valor entre 0 y 180 grados"
            ))
            return False
        
        # Validar velocidad (M04)
        if velocidad not in ['LENTO', 'NORMAL', 'RAPIDO']:
            self.pila_errores.push(Error(
                0, 0, velocidad,
                f"Velocidad '{velocidad}' no reconocida.",
                "SEMÁNTICO (M04)",
                "Use LENTO, NORMAL o RAPIDO"
            ))
            return False
        
        return True

    def _validar_esperar(self, inst):
        """Valida ESPERAR: tiempo positivo."""
        _, ms = inst
        
        if ms <= 0:
            self.pila_errores.push(Error(
                0, 0, str(ms),
                "El tiempo de espera debe ser un número positivo.",
                "SEMÁNTICO",
                "Use ESPERAR con un valor mayor a 0 milisegundos"
            ))
            return False
        
        return True

    def _validar_repetir(self, inst):
        """Valida REPETIR: número de repeticiones positivo (M05)."""
        _, n, _ = inst
        
        if n <= 0:
            self.pila_errores.push(Error(
                0, 0, str(n),
                "El número de repeticiones debe ser mayor que 0.",
                "SEMÁNTICO (M05)",
                "Use REPETIR 1, REPETIR 2, etc."
            ))
            return False
        
        return True

    def _validar_guardar(self, inst):
        """Valida GUARDAR: nombre de rutina único."""
        _, nombre, _ = inst
        
        if nombre in self.rutinas_declaradas:
            self.pila_errores.push(Error(
                0, 0, nombre,
                f"La rutina '{nombre}' ya está definida.",
                "SEMÁNTICO",
                "Use otro nombre o elimine la rutina duplicada"
            ))
            return False
        
        self.rutinas_declaradas.add(nombre)
        return True

    def _validar_ejecutar(self, inst):
        """Valida EJECUTAR: la rutina debe existir (M02)."""
        _, nombre = inst
        
        if nombre not in self.rutinas_declaradas:
            self.pila_errores.push(Error(
                0, 0, nombre,
                f"La rutina '{nombre}' no está declarada.",
                "SEMÁNTICO (M02)",
                f"Declare la rutina con: GUARDAR {nombre} {{ ... }}"
            ))
            return False
        
        return True

    def reiniciar(self):
        """Reinicia el analizador para una nueva ejecución."""
        self.rutinas_declaradas.clear()