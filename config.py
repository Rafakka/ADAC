import os
import sys
import platform
import logging

# Determinar caminho base
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Detectar sistema operacional
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
IS_MAC = platform.system() == "Darwin"

# Caminhos das pastas
CONTATOS_DIR = os.path.join(BASE_DIR, "contatos")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Criar pastas se não existirem
os.makedirs(CONTATOS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Caminho padrão do CSV
CSV_DEFAULT_PATH = os.path.join(CONTATOS_DIR, "contatos.csv")

# Caminho do ADB baseado no SO
ADB_DIR = os.path.join(BASE_DIR, "adb")

if IS_WINDOWS:
    ADB_SUBDIR = os.path.join(ADB_DIR, "Win")
    ADB_PATH = os.path.join(ADB_SUBDIR, "adb.exe")
    
elif IS_LINUX:
    ADB_SUBDIR = os.path.join(ADB_DIR, "Linux")
    ADB_PATH = os.path.join(ADB_SUBDIR, "adb")
    
elif IS_MAC:
    ADB_SUBDIR = os.path.join(ADB_DIR, "Linux")
    ADB_PATH = os.path.join(ADB_SUBDIR, "adb")
    
else:
    ADB_PATH = "adb"

# Verificar se ADB existe na pasta do projeto
if not os.path.exists(ADB_PATH):
    ADB_PATH = "adb"

# Configurações de tempo
TEMPO_DISCAGEM = 8
TEMPO_TRANSFERENCIA = 12