# test_avance2.py - Prueba del Avance 2 (Lexer con autómata)

from lexer import Lexer


def probar_lexer(codigo, nombre_prueba):
    print(f"\n{'='*60}")
    print(f"PRUEBA: {nombre_prueba}")
    print(f"{'='*60}")
    print(f"Código:\n{codigo}\n")
    
    lexer = Lexer(codigo)
    tokens, errores = lexer.obtener_tokens()
    
    print("TOKENS GENERADOS:")
    for token in tokens:
        print(f"  {token}")
    
    if errores.hay_errores():
        print("\nERRORES ENCONTRADOS:")
        errores.mostrar_todos()
    else:
        print("\n✅ Sin errores léxicos")
    
    return tokens, errores


# PRUEBA 1: Código correcto
codigo1 = """
ABRIR;
MOVER 90 RAPIDO;
CERRAR;
GIRAR DERECHA 45;
"""
probar_lexer(codigo1, "Código correcto")


# PRUEBA 2: Error de minúsculas (L02)
codigo2 = """
abrir;
MOVER 90;
"""
probar_lexer(codigo2, "Error L02: minúsculas")


# PRUEBA 3: Ángulo fuera de rango (M01)
codigo3 = """
MOVER 200;
GIRAR DERECHA 190;
"""
probar_lexer(codigo3, "Error M01: ángulo fuera de rango")


# PRUEBA 4: Carácter ilegal (E001)
codigo4 = """
ABRIR@;
MOVER 90#;
"""
probar_lexer(codigo4, "Error E001: carácter ilegal")


# PRUEBA 5: Palabras con mayúsculas y números (identificadores)
codigo5 = """
GUARDAR RUTINA123 {
    ABRIR;
};
EJECUTAR RUTINA123;
"""
probar_lexer(codigo5, "Identificadores con números")


# PRUEBA 6: Comandos con velocidad opcional
codigo6 = """
MOVER 90;
MOVER 45 LENTO;
GIRAR DERECHA 90 RAPIDO;
"""
probar_lexer(codigo6, "Velocidad opcional")


print("\n" + "="*60)
print("FIN DE LAS PRUEBAS DEL AVANCE 2")
print("="*60)