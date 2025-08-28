
import subprocess

from config import ADB_PATH
from logger_manager import log_combined


def verificar_adb():
    """Verifica se o ADB está funcionando"""
    try:
        result = subprocess.run([ADB_PATH, "version"], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            log_combined("ADB não está funcionando corretamente", "error")
            return False
        log_combined(f"ADB encontrado: {result.stdout.splitlines()[0]}", "success")
        return True
    except Exception as e:
        log_combined(f"Erro ao verificar ADB: {e}", "error")
        return False

def detectar_dispositivos():
    """Detecta dispositivos Android conectados"""
    try:
        result = subprocess.run([ADB_PATH, "devices", "-l"], capture_output=True, text=True, timeout=30)
        devices = []
        
        for line in result.stdout.splitlines():
            if "device usb:" in line:
                device_id = line.split()[0]
                devices.append(device_id)
                log_combined(f"Dispositivo detectado: {line}", "success")
        
        return devices if devices else None
        
    except Exception as e:
        log_combined(f"Erro ao detectar dispositivos: {e}", "error")
        return None