# test_final.py
from brazo_esp32 import BrazoESP32
import time

# Cambia COMx por tu puerto
brazo = BrazoESP32(puerto="COM7")

print("Conectando...")
if brazo.conectar():
    print("✅ ESP32 conectado")
    
    print("\n▶️ Probando comandos...")
    brazo.estado()
    time.sleep(0.5)
    
    print("\n▶️ Abriendo pinza...")
    brazo.abrir()
    time.sleep(1)
    
    print("\n▶️ Cerrando pinza...")
    brazo.cerrar()
    time.sleep(1)
    
    print("\n▶️ Moviendo brazo a 90°...")
    brazo.mover(90)
    time.sleep(1)
    
    print("\n▶️ HOME...")
    brazo.home()
    
    brazo.desconectar()
    print("\n✅ Prueba completada")
else:
    print("❌ No se pudo conectar")