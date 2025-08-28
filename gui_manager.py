from config import GUI_ENABLED
from gui_integrada import init_gui
from logger import log_combined

# Instância global para GUI
gui_instance = None

def init_gui_if_enabled():
    """
    Inicializa a GUI se estiver habilitada.
    Retorna tupla: (gui_instance, thread=None)
    """
    global gui_instance
    if GUI_ENABLED:
        gui_instance = init_gui()
        return gui_instance, None  # Thread não usada por enquanto
    return None, None

def update_gui_status_safe(**kwargs):
    """
    Atualiza o status na GUI de forma segura.
    Aceita kwargs:
    status, device, csv, total, processados, sucesso, falha, current
    """
    global gui_instance
    if gui_instance:
        try:
            gui_instance.update_status(**kwargs)
        except Exception as e:
            log_combined(f"Falha ao atualizar GUI: {e}", "error")

def is_gui_paused():
    """Retorna True se GUI estiver pausada"""
    global gui_instance
    return gui_instance and getattr(gui_instance, 'paused', False)

def should_stop():
    """Retorna True se GUI estiver fechada ou loop principal terminado"""
    global gui_instance
    return gui_instance and not getattr(gui_instance, 'running', True)
