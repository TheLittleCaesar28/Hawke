# brazo_esp32.py - Comunicación HAWKE con ESP32

import serial
import serial.tools.list_ports
import time


class BrazoESP32:
    """Controlador del brazo robótico vía ESP32 por puerto serie"""
    
    def __init__(self, puerto=None, baudrate=115200):
        self.serial = None
        self.conectado = False
        self.puerto = puerto
        self.baudrate = baudrate
    
    def listar_puertos(self):
        """Lista los puertos COM disponibles"""
        puertos = serial.tools.list_ports.comports()
        return [(p.device, p.description) for p in puertos]
    
    def conectar(self, puerto=None):
        """Conecta con ESP32 por el puerto especificado"""
        if puerto:
            self.puerto = puerto
        
        if not self.puerto:
            puertos = self.listar_puertos()
            if not puertos:
                print("❌ No se encontraron puertos disponibles")
                return False
            
            print("\n📡 Puertos disponibles:")
            for i, (dev, desc) in enumerate(puertos):
                print(f"   [{i}] {dev} - {desc}")
            
            # Intentar auto-detectar ESP32 (por descripción)
            for dev, desc in puertos:
                if 'USB' in desc or 'CH340' in desc or 'CP210' in desc:
                    self.puerto = dev
                    break
            
            if not self.puerto:
                self.puerto = puertos[0][0]
            
            print(f"\n🔌 Conectando a {self.puerto}...")
        
        try:
            self.serial = serial.Serial(self.puerto, self.baudrate, timeout=2)
            time.sleep(2)  # Esperar a que ESP32 se reinicie
            self.conectado = True
            print(f"✅ Conectado a ESP32 en {self.puerto}")
            
            # Limpiar buffer
            self.serial.reset_input_buffer()
            
            return True
        except Exception as e:
            print(f"❌ Error al conectar: {e}")
            return False
    
    def desconectar(self):
        """Cierra la conexión con ESP32"""
        if self.serial and self.serial.is_open:
            self.serial.close()
            self.conectado = False
            print("✅ Desconectado de ESP32")
    
    def enviar_comando(self, comando):
        """Envía un comando a ESP32 y retorna la respuesta"""
        if not self.conectado or not self.serial:
            print("❌ No conectado a ESP32")
            return None
        
        try:
            # Enviar comando
            self.serial.write(f"{comando}\n".encode())
            time.sleep(0.2)  # Pausa para que ESP32 procese
            
            # Leer respuesta
            respuesta = ""
            timeout = time.time() + 2
            while time.time() < timeout:
                if self.serial.in_waiting:
                    linea = self.serial.readline().decode().strip()
                    if linea:
                        respuesta += linea + "\n"
                time.sleep(0.05)
            
            return respuesta
        except Exception as e:
            print(f"❌ Error al enviar comando: {e}")
            return None
    
    # ============================================================
    #  COMANDOS HAWKE
    # ============================================================
    
    def abrir(self):
        """Envía comando ABRIR"""
        print("  📤 ABRIR")
        return self.enviar_comando("ABRIR")
    
    def cerrar(self):
        """Envía comando CERRAR"""
        print("  📤 CERRAR")
        return self.enviar_comando("CERRAR")
    
    def mover(self, angulo):
        """Envía comando MOVER <ángulo>"""
        if angulo < 0 or angulo > 180:
            print(f"  ❌ Ángulo {angulo} fuera de rango")
            return None
        print(f"  📤 MOVER {angulo}")
        return self.enviar_comando(f"MOVER {angulo}")
    
    def girar(self, direccion, angulo):
        """Envía comando GIRAR <IZQUIERDA|DERECHA> <ángulo>"""
        if angulo < 0 or angulo > 180:
            print(f"  ❌ Ángulo {angulo} fuera de rango")
            return None
        if direccion not in ['IZQUIERDA', 'DERECHA']:
            print(f"  ❌ Dirección {direccion} inválida")
            return None
        print(f"  📤 GIRAR {direccion} {angulo}")
        return self.enviar_comando(f"GIRAR {direccion} {angulo}")
    
    def home(self):
        """Envía comando HOME"""
        print("  📤 HOME")
        return self.enviar_comando("HOME")
    
    def estado(self):
        """Consulta el estado actual del brazo"""
        print("  📤 ESTADO")
        respuesta = self.enviar_comando("ESTADO")
        if respuesta:
            print("  📥 Respuesta:")
            print(respuesta)
        return respuesta
    
    def test(self):
        """Ejecuta una prueba de movimiento"""
        print("\n" + "="*50)
        print("🔧 PRUEBA DE MOVIMIENTO")
        print("="*50)
        
        self.estado()
        time.sleep(0.5)
        
        print("\n▶️ Abriendo pinza...")
        self.abrir()
        time.sleep(1)
        
        print("\n▶️ Cerrando pinza...")
        self.cerrar()
        time.sleep(1)
        
        print("\n▶️ Moviendo brazo a 45°...")
        self.mover(45)
        time.sleep(1)
        
        print("\n▶️ Moviendo brazo a 90°...")
        self.mover(90)
        time.sleep(1)
        
        print("\n▶️ Girando base derecha 45°...")
        self.girar("DERECHA", 45)
        time.sleep(1)
        
        print("\n▶️ Girando base izquierda 45°...")
        self.girar("IZQUIERDA", 45)
        time.sleep(1)
        
        print("\n▶️ HOME...")
        self.home()
        
        print("\n" + "="*50)
        print("✅ PRUEBA COMPLETADA")
        print("="*50)


# ============================================================
#  PRUEBA RÁPIDA (ejecutar directamente)
# ============================================================
if __name__ == "__main__":
    print("="*50)
    print("HAWKE - CONEXIÓN CON ESP32")
    print("="*50)
    
    brazo = BrazoESP32()
    
    if brazo.conectar():
        brazo.test()
        brazo.desconectar()
    else:
        print("\n❌ No se pudo conectar a ESP32")
        print("\nVerifica:")
        print("  1. ESP32 conectado por USB")
        print("  2. El código está subido al ESP32")
        print("  3. El puerto COM correcto")