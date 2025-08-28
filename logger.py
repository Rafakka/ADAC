import logging
from gui_integrada import update_gui_status_safe

# Configuração do logging no console
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

def log_combined(message, level="info", gui=None):
    """
    Loga a mensagem no console e na GUI se gui estiver disponível.
    """
    # Log no console
    if level == "error":
        logging.error(message)
    elif level == "warning":
        logging.warning(message)
    else:
        logging.info(message)

    # Log na GUI se disponível
    if gui:
        gui.add_line(message, level=level)
    else:
        update_gui_status_safe()  # atualiza GUI mesmo sem gui passado, se existir

def mostrar_ajuda_erro(gui=None):
    """Mostra ajuda de solução de problemas"""
    log_combined("", "warning", gui)
    log_combined("🔧 SOLUÇÃO DE PROBLEMAS:", "header", gui)
    log_combined("1. 📱 Conecte o celular via USB", "warning", gui)
    log_combined("2. ⚙️  Ative a depuração USB (Opções do desenvolvedor)", "warning", gui) 
    log_combined("3. ✅ Autorize o computador no popup do celular", "warning", gui)
    log_combined("4. 🔄 Execute: adb devices para testar", "warning", gui)
    log_combined("5. 🚫 Pressione ESC para cancelar", "warning", gui)
    log_combined("", "warning", gui)

def log_final_report(total, sucesso, falha, gui=None):
    """Resumo final do processamento"""
    log_combined("=== ADAC - Processamento concluído ===", "success", gui)
    log_combined(f"📊 Total: {total} contatos", "success", gui)
    log_combined(f"✅ Sucesso: {sucesso}", "success", gui)
    log_combined(f"❌ Falha: {falha}", "warning" if falha > 0 else "success", gui)
