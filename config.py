import os
import sys
import platform
import logging

GUI_ENABLED = True

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
CONFIG_DIR = os.path.join(BASE_DIR, "config")

# Criar pastas se não existirem
os.makedirs(CONTATOS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)

# Caminho do arquivo de configuração
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.txt")

# Configurações padrão
NUMERO_REDIRECIONAMENTO = "11999999999"  # Número padrão para transferência
TEMPO_DISCAGEM = 12
TEMPO_TRANSFERENCIA = 12

# Carregar configurações do arquivo
def carregar_configuracoes():
    """Carrega configurações do arquivo config.txt"""
    config = {
        'numero_redirecionamento': NUMERO_REDIRECIONAMENTO,
        'tempo_discagem': TEMPO_DISCAGEM,
        'tempo_transferencia': TEMPO_TRANSFERENCIA
    }
    
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        key = key.strip().lower()
                        value = value.strip()
                        
                        if key == 'numero_redirecionamento':
                            config['numero_redirecionamento'] = value
                        elif key == 'tempo_discagem':
                            config['tempo_discagem'] = int(value)
                        elif key == 'tempo_transferencia':
                            config['tempo_transferencia'] = int(value)
    except Exception as e:
        logging.error(f"Erro ao carregar configurações: {e}")
    
    return config

# Carregar configurações
configuracoes = carregar_configuracoes()

# Variáveis configuráveis
NUMERO_REDIRECIONAMENTO = configuracoes['numero_redirecionamento']
TEMPO_DISCAGEM = configuracoes['tempo_discagem']
TEMPO_TRANSFERENCIA = configuracoes['tempo_transferencia']

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