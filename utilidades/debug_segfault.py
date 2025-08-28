#!/usr/bin/env python3
"""
Debug para segmentation fault
"""

import faulthandler
import signal
import sys
import os

# Ativar faulthandler para capturar segfaults
faulthandler.enable()

# Registrar handler para SIGSEGV
def segfault_handler(signum, frame):
    print(f"💥 SEGMENTATION FAULT capturado (sinal {signum})")
    print("📋 Stack trace:")
    import traceback
    traceback.print_stack(frame)
    sys.exit(1)

signal.signal(signal.SIGSEGV, segfault_handler)

# Agora importe e execute seu código
print("🔧 Iniciando debug do segmentation fault...")

try:
    from main import main
    main()
except Exception as e:
    print(f"❌ Erro durante execução: {e}")
    import traceback
    traceback.print_exc()
except SystemExit:
    print("✅ Programa encerrado normalmente")