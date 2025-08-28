
import sys
import logging
import os

os.environ['SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR'] = '0'
os.environ['SDL_VIDEO_X11_SHM'] = '0'

from config import LOGS_DIR
from logger import log_combined, mostrar_ajuda_erro, log_final_report
from adb_manager import verificar_adb
from hardware_manager import esperar_celular_conectar
from gui_manager import init_gui_if_enabled, update_gui_status_safe, keep_gui_running
from csv_manager import CSVManager, load_contacts, process_contacts
from caller import discar_e_transferir

# Logging
log_file = os.path.join(LOGS_DIR, 'adac_log.txt')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

def main():
    gui, gui_thread = init_gui_if_enabled()
    log_combined("=== ADAC - Auto Discador iniciado ===")

    try:
        # Verifica ADB
        if not verificar_adb():
            mostrar_ajuda_erro()
            update_gui_status_safe(gui, status="Erro - ADB não disponível")
            return

        # Aguarda celular
        dispositivo = esperar_celular_conectar(gui)
        if not dispositivo:
            log_combined("Operação cancelada pelo usuário", "warning")
            update_gui_status_safe(gui, status="Cancelado pelo usuário")
            return

        # Carrega contatos
        csv_manager, contatos = load_contacts(gui)

        # Processa contatos
        sucesso, falha = process_contacts(contatos, csv_manager, dispositivo, gui)

        # Relatório final
        log_final_report(len(contatos), sucesso, falha)

    except Exception as e:
        log_combined(f"Erro inesperado: {e}", "error")

    finally:
        # Mantém GUI aberta para decisão do usuário
        keep_gui_running(gui, gui_thread)


if __name__ == "__main__":
    main()
