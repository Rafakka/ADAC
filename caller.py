import subprocess
import time
import logging
from config import ADB_PATH, TEMPO_DISCAGEM, TEMPO_TRANSFERENCIA

def executar_comando_adb(comando, device_serial=None):
    """Executa comando ADB com tratamento de erro"""
    try:
        cmd = [ADB_PATH]
        if device_serial:
            cmd.extend(['-s', device_serial])
        cmd.extend(comando.split())
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            logging.error(f"Erro no comando ADB: {result.stderr}")
            return False
        
        return True
    except subprocess.TimeoutExpired:
        logging.error("Timeout ao executar comando ADB")
        return False
    except Exception as e:
        logging.error(f"Exceção ao executar comando ADB: {e}")
        return False

def discar_e_transferir(numero, device_serial=None):
    """Disca número e transfere chamada"""
    try:
        # Abrir aplicativo de telefone
        if not executar_comando_adb(f"shell am start -a android.intent.action.DIAL -d tel:{numero}", device_serial):
            return False
        
        time.sleep(2)  # Aguardar app abrir
        
        # Clicar para discar (ajuste conforme seu dispositivo)
        if not executar_comando_adb("shell input tap 500 1800", device_serial):  # Coordenadas do botão discar
            return False
        
        time.sleep(TEMPO_DISCAGEM)  # Aguardar discagem
        
        # Transferir chamada (tecla de transferência)
        if not executar_comando_adb("shell input keyevent KEYCODE_CALL", device_serial):
            return False
        
        time.sleep(TEMPO_TRANSFERENCIA)  # Aguardar transferência
        
        # Encerrar chamada
        executar_comando_adb("shell input keyevent KEYCODE_ENDCALL", device_serial)
        
        return True
        
    except Exception as e:
        logging.error(f"Erro no processo de discagem: {e}")
        return False