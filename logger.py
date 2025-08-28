
import logging
from gui_integrada import log_message


def log_combined(message, level="info"):
    """Log para ambos GUI e console"""
    global GUI_AVAILABLE
    if GUI_AVAILABLE:
        log_message(message, level)
    
    if level == "error":
        logging.error(message)
    elif level == "warning":
        logging.warning(message)
    else:
        logging.info(message)

def mostrar_ajuda_erro():
    """Mostra ajuda quando ocorre erro"""
    log_combined("", "warning")
    log_combined("🔧 SOLUÇÃO DE PROBLEMAS:", "header")
    log_combined("1. 📱 Conecte o celular via USB", "warning")
    log_combined("2. ⚙️  Ative a depuração USB (Opções do desenvolvedor)", "warning") 
    log_combined("3. ✅ Autorize o computador no popup do celular", "warning")
    log_combined("4. 🔄 Execute: adb devices para testar", "warning")
    log_combined("5. 🚫 Pressione ESC para cancelar", "warning")
    log_combined("", "warning")

def log_final_report(total, sucesso, falha):
    log_combined("=== ADAC - Processamento concluído ===", "success")
    log_combined(f"📊 Total: {total} contatos", "success")
    log_combined(f"✅ Sucesso: {sucesso}", "success")
    log_combined(f"❌ Falha: {falha}", "warning" if falha > 0 else "success")
