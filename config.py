import os
import sys

# Determinar caminho base
if getattr(sys, 'frozen', False):
    # Executável PyInstaller
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Script Python normal
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configurações do ADB
ADB_DIR = os.path.join(BASE_DIR, "adb")
ADB_PATH = os.path.join(ADB_DIR, "adb.exe")
ADB_PATH = os.environ.get('ADB_PATH', 'adb')

if not os.path.exists(ADB_PATH):
    ADB_PATH = "adb"  # Fallback para ADB do sistema

# Configurações de tempo (ajustados para CALL intent)
TEMPO_DISCAGEM = 8
TEMPO_TRANSFERENCIA = 12 

# Configurações do dispositivo
DEVICE_SERIAL = os.environ.get('DEVICE_SERIAL', '')

# Configurações de CSV
CSV_DEFAULT_PATH = os.environ.get('CSV_PATH', 'contatos.csv')