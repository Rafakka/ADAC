import subprocess
import time
import logging

def discar_inteligente(numero, device_serial):
    """Método inteligente usando comandos AT via ADB"""
    try:
        logging.info("Usando método inteligente de discagem...")
        
        # 1. Abrir atividade de discagem
        subprocess.run([
            "adb", "-s", device_serial, "shell", "am", "start",
            "-a", "android.intent.action.CALL",
            "-d", f"tel:{numero}"
        ], check=True)
        time.sleep(3)
        
        # 2. Método alternativo: usar input text com ; (finalizador de discagem)
        # Isso pode discar automaticamente em alguns dispositivos
        subprocess.run([
            "adb", "-s", device_serial, "shell", "input", "text", f"{number};"
        ], check=True)
        time.sleep(2)
        
        # 3. Se não discou, tentar ENTER
        subprocess.run([
            "adb", "-s", device_serial, "shell", "input", "keyevent", "KEYCODE_ENTER"
        ], check=True)
        time.sleep(2)
        
        # 4. Último recurso: tentar todas as coordenadas possíveis
        coordenadas = [
            (500, 2050), (500, 2100), (500, 2150),
            (540, 2050), (540, 2100), (540, 2150),
            (580, 2050), (580, 2100), (580, 2150),
        ]
        
        for x, y in coordenadas:
            subprocess.run([
                "adb", "-s", device_serial, "shell", "input", "tap", str(x), str(y)
            ], check=True)
            time.sleep(2)
            
            # Verificar se discou
            result = subprocess.run([
                "adb", "-s", device_serial, "shell", "dumpsys", "telephony.registry"
            ], capture_output=True, text=True)
            
            if "mCallState=2" in result.stdout:
                return True
        
        return False
        
    except Exception as e:
        logging.error(f"Erro no método inteligente: {e}")
        return False