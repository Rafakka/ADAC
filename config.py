import os

# Configurações do ADB
ADB_PATH = os.environ.get('ADB_PATH', 'adb')

# Configurações de tempo
TEMPO_DISCAGEM = 15  # segundos para aguardar a discagem
TEMPO_TRANSFERENCIA = 10  # segundos para aguardar transferência

# Configurações do dispositivo
DEVICE_SERIAL = os.environ.get('DEVICE_SERIAL', '')

# Configurações de CSV
CSV_DEFAULT_PATH = os.environ.get('CSV_PATH', '/app/contatos/contatos.csv')