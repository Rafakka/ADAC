
import logging

# Logging console
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

gui_instance = None  # Será setado por gui_integrada

def set_gui(gui):
    global gui_instance
    gui_instance = gui

def log_combined(message, level="info", gui=None):
    """Log para console e GUI se disponível"""
    # Log no console
    if level == "error":
        logging.error(message)
    elif level == "warning":
        logging.warning(message)
    elif level == "success":
        logging.info(f"[SUCCESS] {message}")
    else:
        logging.info(message)
    
    # Log na GUI
    gui_to_use = gui if gui else gui_instance
    if gui_to_use:
        gui_to_use.add_line(message, level=level)

def mostrar_ajuda_erro(gui=None):
    """Mostra ajuda quando ocorre erro"""
    mensagens = [
        "🔧 SOLUÇÃO DE PROBLEMAS:",
        "1. 📱 Conecte o celular via USB",
        "2. ⚙️  Ative a depuração USB (Opções do desenvolvedor)",
        "3. ✅ Autorize o computador no popup do celular",
        "4. 🔄 Execute: adb devices para testar",
        "5. 🚫 Pressione ESC para cancelar"
    ]
    for m in mensagens:
        log_combined(m, "warning", gui)

def log_final_report(total, sucesso, falha, gui=None):
    log_combined("=== ADAC - Processamento concluído ===", "success", gui)
    log_combined(f"📊 Total: {total} contatos", "success", gui)
    log_combined(f"✅ Sucesso: {sucesso}", "success", gui)
    log_combined(f"❌ Falha: {falha}", "warning" if falha > 0 else "success", gui)
