import os
import sys
import platform
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('autodialer.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Determinar caminho base
if getattr(sys, 'frozen', False):
    # Executável PyInstaller
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Script Python normal
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Detectar sistema operacional
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
IS_MAC = platform.system() == "Darwin"

logging.info(f"Sistema operacional detectado: {platform.system()}")

# Caminho do ADB baseado no SO
ADB_DIR = os.path.join(BASE_DIR, "adb")

if IS_WINDOWS:
    ADB_SUBDIR = os.path.join(ADB_DIR, "Win")
    ADB_PATH = os.path.join(ADB_SUBDIR, "adb.exe")
    logging.info("Usando ADB para Windows")
    
elif IS_LINUX:
    ADB_SUBDIR = os.path.join(ADB_DIR, "Linux")
    ADB_PATH = os.path.join(ADB_SUBDIR, "adb")
    logging.info("Usando ADB para Linux")
    
elif IS_MAC:
    ADB_SUBDIR = os.path.join(ADB_DIR, "Linux")  # Mac usa mesmo binário que Linux
    ADB_PATH = os.path.join(ADB_SUBDIR, "adb")
    logging.info("Usando ADB para Mac (Linux)")
    
else:
    ADB_PATH = "adb"  # Fallback
    logging.warning("Sistema operacional não identificado, usando ADB do sistema")

# Verificar se ADB existe na pasta do projeto
if os.path.exists(ADB_PATH):
    logging.info(f"ADB encontrado em: {ADB_PATH}")
    
    # Dar permissão de execução no Linux/Mac
    if not IS_WINDOWS:
        try:
            os.chmod(ADB_PATH, 0o755)
            logging.info("Permissões de execução concedidas ao ADB")
        except Exception as e:
            logging.warning(f"Não foi possível dar permissão ao ADB: {e}")
else:
    logging.warning(f"ADB não encontrado em {ADB_PATH}, usando ADB do sistema")
    ADB_PATH = "adb"  # Fallback para ADB do sistema

# Configurações de tempo
TEMPO_DISCAGEM = 8
TEMPO_TRANSFERENCIA = 12

# Configurações de CSV
CSV_DEFAULT_PATH = os.path.join(BASE_DIR, "contatos.csv")