import subprocess
import logging
from config import ADB_PATH
from gui_manager import GUI_AVAILABLE

def verificar_adb():
    """Verifica se ADB está acessível"""
    try:
        result = subprocess.run([ADB_PATH, "version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            logging.info(f"ADB disponível: {result.stdout.strip()}")
            return True
        else:
            logging.error("ADB não retornou versão corretamente")
            return False
    except Exception as e:
        logging.error(f"Erro ao verificar ADB: {e}")
        return False
    
    