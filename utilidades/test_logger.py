#!/usr/bin/env python3
"""Teste do sistema de logging"""

from logger_manager import log_combined, init_gui_logger

print("🧪 Testando sistema de logging...")

# Teste sem GUI
init_gui_logger(False)
log_combined("Teste sem GUI - deve aparecer só no console", "info")
log_combined("Teste de erro sem GUI", "error")
log_combined("Teste de warning sem GUI", "warning")

# Teste com GUI (simulado)
init_gui_logger(True)
log_combined("Teste com GUI - deve tentar logar na GUI", "success")

print("✅ Teste concluído! Verifique o console e o arquivo de log.")