# test_avance3.py - Prueba del Avance 3 (Parser + GUI básica)

from lexer import Lexer
from parser import Parser

def probar_parser(codigo, nombre_prueba):
    print(f"\n{'='*60}")
    print(f"PRUEBA: {nombre_prueba}")
    print(f"{'='*60}")
    print(f"Código:\n{codigo}\n")
    
    # FASE 1: ANÁLISIS LÉXICO
    print("FASE 1: ANÁLISIS LÉXICO")
    lexer = Lexer(codigo)
    tokens, errores_lex = lexer.obtener_tokens()
    
    if errores_lex.hay_errores():
        print("Error léxico detectado:")
        errores_lex.mostrar_todos()
        return False
    
    print(f"{len(tokens)} tokens generados")
    for t in tokens:
        print(f"   {t}")
    
    # FASE 2: ANÁLISIS SINTÁCTICO
    print("\nFASE 2: ANÁLISIS SINTÁCTICO")
    parser = Parser(tokens)
    instrucciones, errores_sint = parser.parse()
    
    if errores_sint.hay_errores():
        print("Error sintáctico/semántico detectado:")
        errores_sint.mostrar_todos()
        return False
    
    print(f" {len(instrucciones)} instrucciones reconocidas")
    
    print("\nINSTRUCCIONES GENERADAS:")
    for i, inst in enumerate(instrucciones, 1):
        print(f"   {i}. {inst}")
    
    print("\nPRUEBA EXITOSA")
    return True



# PRUEBA 1: Código correcto
codigo1 = """
ABRIR;
CERRAR;
MOVER 90 RAPIDO;
GIRAR DERECHA 45;
"""

probar_parser(codigo1, "Código correcto")


# PRUEBA 2: Rutinas (GUARDAR y EJECUTAR)
codigo2 = """
GUARDAR SALUDO {
    MOVER 30 LENTO;
    CERRAR;
};

EJECUTAR SALUDO;
"""

probar_parser(codigo2, "Rutinas (GUARDAR y EJECUTAR)")


# PRUEBA 3: REPETIR
codigo3 = """
REPETIR 3 {
    ABRIR;
    CERRAR;
};
"""

probar_parser(codigo3, "REPETIR")


# PRUEBA 4: Error sintáctico (falta ';')
codigo4 = """
ABRIR
CERRAR;
"""

probar_parser(codigo4, "Error: falta ';' después de ABRIR")


# PRUEBA 5: Error semántico (rutina no definida)
codigo5 = """
EJECUTAR RUTINA_INEXISTENTE;
"""

probar_parser(codigo5, "Error: rutina no definida (M02)")


# PRUEBA 6: Error semántico (REPETIR con 0)
codigo6 = """
REPETIR 0 {
    ABRIR;
};
"""

probar_parser(codigo6, "Error: REPETIR 0 (M05)")


print("\n" + "="*60)
print("FIN DE LAS PRUEBAS DEL AVANCE 3")
print("="*60)