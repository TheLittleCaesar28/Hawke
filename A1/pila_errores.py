#  HAWKE - Pila de Errores
#  Almacena y reporta errores lexicos y sintacticos


class Error:
    """
    Representa un error encontrado durante el analisis.
    Contiene toda la informacion necesaria para reportarlo al usuario.
    """
    def __init__(self, linea, columna, token, descripcion, tipo, solucion):
        self.linea       = linea
        self.columna     = columna
        self.token       = token
        self.descripcion = descripcion
        self.tipo        = tipo        # "LEXICO", "SINTACTICO", "SEMANTICO"
        self.solucion    = solucion

    def __str__(self):
        return (f"[{self.tipo}] Linea {self.linea}, Col {self.columna} "
                f"-> '{self.token}': {self.descripcion}")


class PilaErrores:
    """
    Pila LIFO para almacenar errores durante el analisis.
    Los errores mas recientes se muestran primero.
    """

    def __init__(self):
        self.pila = []

    def push(self, error):
        """Agrega un nuevo error a la cima de la pila."""
        self.pila.append(error)

    def pop(self):
        """Elimina y devuelve el error mas reciente."""
        if self.pila:
            return self.pila.pop()
        return None

    def peek(self):
        """Devuelve el error mas reciente sin eliminarlo."""
        if self.pila:
            return self.pila[-1]
        return None

    def vacia(self):
        """Retorna True si no hay errores."""
        return len(self.pila) == 0

    def hay_errores(self):
        """Retorna True si hay al menos un error."""
        return len(self.pila) > 0

    def total(self):
        """Retorna el numero total de errores."""
        return len(self.pila)

    def limpiar(self):
        """Vacia completamente la pila."""
        self.pila = []

    def mostrar_todos(self):
        """Muestra todos los errores en orden (del primero al ultimo)."""
        if self.vacia():
            print("Sin errores.")
            return
        print(f"\n{'='*55}")
        print(f"PILA DE ERRORES  ({self.total()} errores encontrados)")
        print(f"{'='*55}")
        for i, error in enumerate(self.pila, 1):
            print(f"\n  [{i}] {error}")
            print(f"       Sugerencia: {error.solucion}")

    def como_texto(self):
        """Retorna todos los errores como string (para mostrar en GUI)."""
        if self.vacia():
            return "Sin errores."
        lineas = []
        for i, error in enumerate(self.pila, 1):
            lineas.append(f"[{i}] {error}")
            lineas.append(f"     Sugerencia: {error.solucion}\n")
        return "\n".join(lineas)


#  PRUEBA DE LA PILA DE ERRORES
if __name__ == "__main__":
    print("="*60)
    print("PRUEBA DE LA PILA DE ERRORES")
    print("="*60)
    
    # Crear pila de errores
    pila = PilaErrores()
    
    # Verificar que está vacía
    print(f"\n¿Pila vacía? {pila.vacia()}")
    print(f"Total de errores: {pila.total()}")
    
    # Crear errores de ejemplo
    print("\n>>> Agregando errores...")
    
    error1 = Error(1, 1, "abrir", "Minúscula prohibida", "LÉXICO (L02)", "Escriba 'ABRIR'")
    pila.push(error1)
    print(f"  Error agregado: {error1}")
    
    error2 = Error(2, 5, "MOVER", "Falta ángulo", "SINTÁCTICO (S03)", "Use MOVER <ángulo>")
    pila.push(error2)
    print(f"  Error agregado: {error2}")
    
    error3 = Error(3, 7, "200", "Ángulo fuera de rango", "SEMÁNTICO (M01)", "Use valores entre 0 y 180")
    pila.push(error3)
    print(f"  Error agregado: {error3}")
    
    # Mostrar total
    print(f"\nTotal de errores después de push: {pila.total()}")
    print(f"¿Hay errores? {pila.hay_errores()}")
    
    # Mostrar todos los errores
    pila.mostrar_todos()
    
    # Probar peek (ver último error sin eliminar)
    print(f"\n>>> peek(): {pila.peek()}")
    
    # Probar pop (eliminar último error)
    print(f"\n>>> pop(): {pila.pop()}")
    print(f"Total de errores después de pop: {pila.total()}")
    
    # Mostrar errores restantes
    pila.mostrar_todos()
    
    # Probar como_texto()
    print("\n>>> como_texto():")
    print(pila.como_texto())
    
    # Limpiar pila
    print("\n>>> Limpiando pila...")
    pila.limpiar()
    print(f"¿Pila vacía después de limpiar? {pila.vacia()}")
    
    print("\n PILA DE ERRORES FUNCIONANDO CORRECTAMENTE")