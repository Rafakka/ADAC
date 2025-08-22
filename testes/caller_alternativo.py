import subprocess
import time
import logging
from config import ADB_PATH

def discar_alternativo(numero, device_serial=None):
    """Métodos alternativos para discar"""
    
    # Método 1: Usar KEYCODE_CALL (pode discar automaticamente)
    try:
        logging.info("Tentando método KEYCODE_CALL...")
        subprocess.run([
            ADB_PATH, "-s", device_serial, "shell", "input", "keyevent", "KEYCODE_CALL"
        ], check=True)
        time.sleep(3)
        return True
    except:
        logging.warning("KEYCODE_CALL não funcionou")
    
    # Método 2: Usar Accessibility Service (se disponível)
    try:
        logging.info("Tentando acessibilidade...")
        # Habilitar talkback temporariamente (pode variar)
        subprocess.run([
            ADB_PATH, "-s", device_serial, "shell", "settings", "put", "secure", 
            "enabled_accessibility_services", 
            "com.google.android.marvin.talkback/com.google.android.marvin.talkback.TalkBackService"
        ], check=True)
        time.sleep(2)
        
        # Navegar até o botão discar
        subprocess.run([
            ADB_PATH, "-s", device_serial, "shell", "input", "keyevent", "KEYCODE_TAB"
        ], check=True)
        time.sleep(1)
        
        subprocess.run([
            ADB_PATH, "-s", device_serial, "shell", "input", "keyevent", "KEYCODE_ENTER"
        ], check=True)
        
        return True
    except:
        logging.warning("Método de acessibilidade não funcionou")
    
    # Método 3: Swipe ou gestos
    try:
        logging.info("Tentando gestos...")
        # Fazer swipe para cima no botão (pode variar)
        subprocess.run([
            ADB_PATH, "-s", device_serial, "shell", "input", "swipe", "540", "2000", "540", "1900", "100"
        ], check=True)
        return True
    except:
        logging.warning("Método de gestos não funcionou")
    
    return False

def usar_ui_automator(device_serial):
    """Usar UIAutomator para encontrar e clicar no botão"""
    try:
        # Encontrar botão por texto ou descrição
        result = subprocess.run([
            ADB_PATH, "-s", device_serial, "shell", 
            "uiautomator", "dump", "/sdcard/ui.xml"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # Procurar por botão de discar no XML
            subprocess.run([
                ADB_PATH, "-s", device_serial, "pull", "/sdcard/ui.xml"
            ])
            
            # Analisar XML para encontrar coordenadas do botão
            # (implementar parsing do XML aqui)
            
            return True
    except:
        logging.warning("UIAutomator não disponível")
    
    return False