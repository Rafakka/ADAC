import logging
from config import GUI_ENABLED
from logger import log_combined, mostrar_ajuda_erro, log_final_report
from hardware_manager import esperar_celular_conectar
from gui_manager import init_gui_if_enabled, update_gui_status_safe
from csv_manager import load_contacts, process_contacts
from adb_manager import verificar_adb

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

def main():
    # Inicializa GUI se habilitada
    gui, gui_thread = init_gui_if_enabled()

    # Atualiza status inicial na GUI
    update_gui_status_safe(status="Inicializando...")

    # Log de início
    log_combined("=== ADAC - Auto Discador iniciado ===", gui=gui)

    # Verifica se ADB está disponível
    if not verificar_adb():
        mostrar_ajuda_erro(gui)
        return

    # Espera até que celular seja conectado
    celular = esperar_celular_conectar(gui)
    if not celular:
        log_combined("Operação cancelada pelo usuário", "warning", gui)
        return

    # Carrega contatos do CSV
    contatos = load_contacts("contatos.csv")
    if not contatos:
        log_combined("Nenhum contato encontrado no CSV", "warning", gui)
        return

    # Processa contatos
    sucesso, falha = process_contacts(contatos, celular, gui)

    # Relatório final
    log_final_report(len(contatos), sucesso, falha, gui)

    # Mantém a GUI aberta até que usuário pressione ESC
    if gui:
        gui.wait_for_escape_safe()

if __name__ == "__main__":
    main()
