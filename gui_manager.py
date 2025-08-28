from gui_integrada import init_gui_if_enabled
from logger import set_gui

gui_instance = None

def init_gui():
    """Inicializa GUI e conecta ao logger"""
    global gui_instance
    gui_instance = init_gui_if_enabled()
    if gui_instance:
        set_gui(gui_instance)
    return gui_instance

def update_gui_status_safe(**kwargs):
    """Atualiza status da GUI se estiver ativa"""
    if gui_instance:
        gui_instance.update_status(**kwargs)
