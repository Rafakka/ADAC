import os

# Configurações do ADB
ADB_PATH = os.environ.get('ADB_PATH', 'adb')

# Configurações de tempo (ajustados para CALL intent)
TEMPO_DISCAGEM = 8  # Menos tempo necessário pois disca automaticamente
TEMPO_TRANSFERENCIA = 12  # Tempo para transferência

# Configurações do dispositivo
DEVICE_SERIAL = os.environ.get('DEVICE_SERIAL', '')

# Configurações de CSV
CSV_DEFAULT_PATH = os.environ.get('CSV_PATH', 'contatos.csv')