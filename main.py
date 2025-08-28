import subprocess
import sys
import threading
import time as time_module  # Renomear para evitar conflito
import logging
import os
import pygame

os.environ['SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR'] = '0'
os.environ['SDL_VIDEO_X11_SHM'] = '0'  # Desativa shared memory

from csv_manager import CSVManager, encontrar_arquivo_csv, load_contacts, process_contacts
from caller import discar_e_transferir
from config import ADB_PATH, CONTATOS_DIR, LOGS_DIR, CSV_DEFAULT_PATH, GUI_ENABLED
from logger import log_combined, mostrar_ajuda_erro, log_final_report
from adb_manager import verificar_adb
from hardware_manager import detectar_dispositivos, esperar_celular_conectar
from gui_manager import init_gui_if_enabled, update_gui_status_safe, keep_gui_running

# Configuração de GUI - usar variável global
GUI_AVAILABLE = False
if GUI_ENABLED:
    try:
        from gui_integrada import init_gui, log_message, update_gui_status, is_gui_paused, should_stop
        GUI_AVAILABLE = True
    except ImportError as e:
        print(f"GUI não disponível: {e}")
        GUI_AVAILABLE = False

# Configuração de logging tradicional
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

    if not verificar_adb():
        mostrar_ajuda_erro()
        update_gui_status_safe(gui, status="Erro - ADB não disponível")
        keep_gui_running(gui, gui_thread)
        return

    celular = esperar_celular_conectar(gui)
    if not celular:
        log_combined("Operação cancelada pelo usuário", "warning")
        update_gui_status_safe(gui, status="Cancelado pelo usuário")
        keep_gui_running(gui, gui_thread)
        return

    csv_manager, contatos = load_contacts(gui)
    sucesso, falha = process_contacts(contatos, csv_manager, celular, gui)
    log_final_report(len(contatos), sucesso, falha)
    keep_gui_running(gui, gui_thread)


if __name__ == "__main__":
    main()