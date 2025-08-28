import subprocess

from config import ADB_PATH
from gui_integrada import update_gui_status
from logger import log_combined, mostrar_ajuda_erro
from main import GUI_AVAILABLE


def verificar_adb():
    """Verifica se o ADB está funcionando - NÃO USA sys.exit()"""
    try:
        result = subprocess.run([ADB_PATH, "version"], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            log_combined("ADB não está funcionando corretamente", "error")
            return False
        log_combined(f"ADB encontrado: {result.stdout.splitlines()[0]}", "success")
        return True
    except Exception as e:
        log_combined(f"Erro ao verificar ADB: {e}", "error")
        return False  # Retorna False, não sai do programa

if not verificar_adb():
    log_combined("ADB não disponível.", "error")
    mostrar_ajuda_erro()  # 👈 Mostra ajuda
    if GUI_AVAILABLE:
        update_gui_status(status="Erro - ADB não disponível")
    execution_successful = False