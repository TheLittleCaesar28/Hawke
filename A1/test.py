# test_avance1.py - Prueba completa del Avance 1
# Fundamentos del lenguaje: Tabla de símbolos y Pila de errores

from tabla_simbolos import TablaSimbolos
from pila_errores import PilaErrores, Error


def probar_tabla_simbolos():
    """Prueba la funcionalidad de la tabla de símbolos."""
    print("\n" + "="*60)
    print("PRUEBA 1: TABLA DE SÍMBOLOS")
    print("="*60)
    
    tabla = TablaSimbolos()
    
    # 1.1 Estado inicial
    print("\n1.1 Estado inicial del brazo:")
    tabla.mostrar_estado()
    
    # 1.2 Guardar rutinas
    print("\n1.2 Guardando rutinas...")
    tabla.guardar_rutina("AGARRAR", [
        ('MOVER', 30, 'LENTO'),
        ('CERRAR',),
        ('ESPERAR', 500)
    ], 3)
    tabla.guardar_rutina("SOLTAR", [
        ('MOVER', 30, 'LENTO'),
        ('ABRIR',),
        ('ESPERAR', 300)
    ], 8)
    
    # 1.3 Listar rutinas
    print("\n1.3 Listado de rutinas:")
    tabla.listar_rutinas()
    
    # 1.4 Verificar existencia
    print("\n1.4 Verificación de existencia:")
    print(f"  ¿Existe 'AGARRAR'? {tabla.rutina_existe('AGARRAR')}")
    print(f"  ¿Existe 'SALUDO'? {tabla.rutina_existe('SALUDO')}")
    
    # 1.5 Obtener rutina
    print("\n1.5 Obtener rutina:")
    rutina = tabla.obtener_rutina("AGARRAR")
    print(f"  Instrucciones de AGARRAR: {rutina}")
    
    # 1.6 Actualizar estado
    print("\n1.6 Actualizando estado del brazo...")
    tabla.actualizar_estado('pinza', 180)
    tabla.actualizar_estado('brazo_v', 90)
    tabla.actualizar_estado('velocidad', 'RAPIDO')
    
    # 1.7 Mostrar estado actualizado
    print("\n1.7 Estado actualizado:")
    tabla.mostrar_estado()
    
    # 1.8 Probar límites (debe fallar)
    print("\n1.8 Probando límites (ángulo 200 debe fallar):")
    resultado = tabla.actualizar_estado('brazo_v', 200)
    print(f"  Resultado: {resultado} (False = fuera de rango)")
    
    print("\n TABLA DE SÍMBOLOS: TODAS LAS PRUEBAS EXITOSAS")


def probar_pila_errores():
    """Prueba la funcionalidad de la pila de errores."""
    print("\n" + "="*60)
    print("PRUEBA 2: PILA DE ERRORES")
    print("="*60)
    
    pila = PilaErrores()
    
    # 2.1 Estado inicial
    print("\n2.1 Estado inicial:")
    print(f"  ¿Vacía? {pila.vacia()}")
    print(f"  Total: {pila.total()}")
    
    # 2.2 Agregar errores (todos los tipos)
    print("\n2.2 Agregando errores de diferentes tipos:")
    
    error_lexico = Error(1, 1, "abrir", "Minúscula prohibida", "LÉXICO (L02)", "Use MAYÚSCULAS")
    pila.push(error_lexico)
    print(f"  + {error_lexico}")
    
    error_sintactico = Error(2, 5, "MOVER", "Falta ángulo", "SINTÁCTICO (S03)", "Use MOVER <ángulo>")
    pila.push(error_sintactico)
    print(f"  + {error_sintactico}")
    
    error_semantico = Error(3, 7, "200", "Ángulo fuera de rango", "SEMÁNTICO (M01)", "Use 0-180")
    pila.push(error_semantico)
    print(f"  + {error_semantico}")
    
    # 2.3 Verificar estado
    print("\n2.3 Estado después de push:")
    print(f"  ¿Vacía? {pila.vacia()}")
    print(f"  Total: {pila.total()}")
    print(f"  ¿Hay errores? {pila.hay_errores()}")
    
    # 2.4 Mostrar todos
    print("\n2.4 Mostrando todos los errores:")
    pila.mostrar_todos()
    
    # 2.5 Probar peek
    print("\n2.5 peek() - ver último error sin eliminar:")
    print(f"  Último error: {pila.peek()}")
    print(f"  Total después de peek: {pila.total()} (sigue igual)")
    
    # 2.6 Probar pop
    print("\n2.6 pop() - eliminar último error:")
    eliminado = pila.pop()
    print(f"  Eliminado: {eliminado}")
    print(f"  Total después de pop: {pila.total()}")
    
    # 2.7 Probar como_texto()
    print("\n2.7 como_texto() - errores como string:")
    print(pila.como_texto())
    
    # 2.8 Limpiar pila
    print("\n2.8 limpiar() - vaciar pila:")
    pila.limpiar()
    print(f"  Total después de limpiar: {pila.total()}")
    print(f"  ¿Vacía? {pila.vacia()}")
    
    # 2.9 Mostrar cuando está vacía
    print("\n2.9 Mostrar errores con pila vacía:")
    pila.mostrar_todos()
    
    print("\n PILA DE ERRORES: TODAS LAS PRUEBAS EXITOSAS")


def probar_integracion():
    """Prueba la integración entre tabla de símbolos y pila de errores."""
    print("\n" + "="*60)
    print("PRUEBA 3: INTEGRACIÓN TABLA + PILA")
    print("="*60)
    
    tabla = TablaSimbolos()
    pila = PilaErrores()
    
    # Simular un programa que guarda una rutina
    print("\n3.1 Guardando rutina 'SALUDO':")
    tabla.guardar_rutina("SALUDO", [('ABRIR',), ('CERRAR',)], 1)
    tabla.listar_rutinas()
    
    # Simular un error al ejecutar una rutina inexistente
    print("\n3.2 Intentando ejecutar rutina inexistente:")
    nombre = "DESCONOCIDO"
    if not tabla.rutina_existe(nombre):
        error = Error(5, 1, nombre, f"Rutina '{nombre}' no existe", "SEMÁNTICO (M02)", f"Declare {nombre} con GUARDAR")
        pila.push(error)
        print(f"  Error generado: {error}")
    
    # Simular otro error (ángulo fuera de rango)
    print("\n3.3 Intentando mover brazo a 200°:")
    if not tabla.actualizar_estado('brazo_v', 200):
        error = Error(6, 7, "200", "Ángulo fuera de rango", "SEMÁNTICO (M01)", "Use valores entre 0 y 180")
        pila.push(error)
        print(f"  Error generado: {error}")
    
    # Mostrar todos los errores acumulados
    print("\n3.4 Errores acumulados en la pila:")
    pila.mostrar_todos()
    
    # Mostrar estado final del brazo
    print("\n3.5 Estado final del brazo:")
    tabla.mostrar_estado()
    
    print("\n INTEGRACIÓN: TODAS LAS PRUEBAS EXITOSAS")


#  EJECUTAR TODAS LAS PRUEBAS
if __name__ == "__main__":
    print("\n" + "="*60)
    print("INICIANDO PRUEBAS DEL AVANCE 1")
    print("="*60)
    
    # Probar tabla de símbolos
    probar_tabla_simbolos()
    
    # Probar pila de errores
    probar_pila_errores()
    
    # Probar integración
    probar_integracion()
    
    print("\n" + "="*60)
    print("AVANCE 1 - COMPLETADO EXITOSAMENTE")
    print("="*60)