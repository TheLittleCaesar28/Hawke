# demo

from demo.lexer_ import Lexer
from parser import Parser
from tabla_simbolos import TablaSimbolos

def ejecutar(codigo):
    print("="*60)
    print("HAWKE")
    print("="*60)
    print(f"\nCÓDIGO:\n{codigo}\n")
    
    # 1. Análisis léxico
    print("FASE 1: LEXER")
    lexer = Lexer(codigo)
    tokens, errores_lex = lexer.obtener_tokens()
    
    if errores_lex.hay_errores():
        print("ERRORES LÉXICOS:")
        errores_lex.mostrar_todos()
        return
    
    print(f" {len(tokens)} tokens generados")
    for t in tokens:
        print(f"   {t}")
    
    # 2. Análisis sintáctico
    print("\nFASE 2: PARSER")
    parser = Parser(tokens)
    instrucciones, errores_par = parser.parse()
    
    if errores_par.hay_errores():
        print(" ERRORES SINTÁCTICOS:")
        errores_par.mostrar_todos()
        return
    
    print(f" {len(instrucciones)} instrucciones reconocidas")
    for i in instrucciones:
        print(f"   {i}")
    
    print("\n ANÁLISIS COMPLETADO SIN ERRORES")

# Prueba 1: Código correcto
codigo1 = """
ABRIR;
MOVER 90 RAPIDO;
CERRAR;
"""

ejecutar(codigo1)

# Prueba 2: Código con errores
codigo2 = """
abrir;      // minúscula
MOVER 200;  // ángulo fuera de rango
"""

ejecutar(codigo2)