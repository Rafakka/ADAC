import subprocess
from config import ADB_PATH
from logger import log_combined

def verificar_adb():
    """Verifica se ADB está acessível"""
    try:
        result = subprocess.run([ADB_PATH,"version"], capture_output=True, text=True, timeout=5)
        log_combined(f"ADB OK: {result.stdout.strip()}", "success")
        return True
    except Exception as e:
        log_combined(f"Erro: ADB não encontrado ({e})", "error")
        return False
