
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