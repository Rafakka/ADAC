import logging
import os
from config import LOGS_DIR, GUI_ENABLED

# Configuração do logger
log_file = os.path.join(LOGS_DIR, 'adac_log.txt')

# Criar diretório de logs se não existir
os.makedirs(LOGS_DIR, exist_ok=True)

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Variável para controlar se GUI está disponível
GUI_AVAILABLE = False

def init_gui_logger(gui_available):
    """Inicializa o logger com status da GUI"""
    global GUI_AVAILABLE
    GUI_AVAILABLE = gui_available

def log_combined(message, level="info"):
    """
    Log para ambos GUI e console
    """
    global GUI_AVAILABLE
    
    # Log tradicional (sempre funciona)
    if level == "error":
        logging.error(message)
    elif level == "warning":
        logging.warning(message)
    else:
        logging.info(message)
    
    # Log na GUI (se disponível)
    if GUI_AVAILABLE:
        try:
            from gui_integrada import log_message
            log_message(message, level)
        except ImportError:
            # GUI não disponível, ignora silenciosamente
            pass
        except Exception as e:
            # Erro ao logar na GUI, mas não quebra o sistema
            logging.error(f"Erro ao logar na GUI: {e}")

def setup_logging():
    """Configuração completa do logging"""
    # Garantir que o diretório de logs existe
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    # Configurar handlers personalizados
    logger = logging.getLogger()
    logger.handlers.clear()  # Remover handlers padrão
    
    # Handler para arquivo
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    
    # Adicionar handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)
    
    return logger

# Inicializar logging
logger = setup_logging()