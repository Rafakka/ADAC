from config import GUI_ENABLED, CSV_PATH
from logger import log_combined, mostrar_ajuda_erro, log_final_report
from gui_manager import init_gui, update_gui_status_safe
from hardware_manager import esperar_celular_conectar
from csv_manager import load_contacts, process_contacts
from adb_manager import verificar_adb

def main():
    gui = init_gui() if GUI_ENABLED else None
    update_gui_status_safe(status="Inicializando...")

    if not verificar_adb():
        mostrar_ajuda_erro(gui)
        return

    celular = esperar_celular_conectar(gui)
    if not celular:
        log_combined("Operação cancelada pelo usuário", "warning", gui)
        return

    contatos = load_contacts(CSV_PATH, gui)
    sucesso, falha = process_contacts(contatos, celular, gui)
    log_final_report(len(contatos), sucesso, falha, gui)

    if gui:
        gui.run()

if __name__=="__main__":
    main()
