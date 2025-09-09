import subprocess
import time
import logging
import os
from config import ADB_PATH, TEMPO_TRANSFERENCIA, NUMERO_REDIRECIONAMENTO

def executar_comando_adb(comando, device_serial=None):
    try:
        cmd = [ADB_PATH]
        if device_serial:
            cmd.extend(['-s', device_serial])
        
        if isinstance(comando, str):
            cmd.extend(comando.split())
        else:
            cmd.extend(comando)
        
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0
        
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30, startupinfo=startupinfo
        )
        
        if result.returncode != 0:
            logging.error(f"Erro no comando ADB: {result.stderr}")
            return False
        
        return True
    except Exception as e:
        logging.error(f"Exceção ao executar comando ADB: {e}")
        return False

def enviar_dtmf(numero, device_serial):
    """Envia os dígitos do número como DTMF durante a chamada"""
    for digit in numero:
        # KEYCODE_DPAD emula DTMF: precisa mapear dígitos 0-9
        if digit.isdigit():
            keycode = f"KEYCODE_{digit}"
            executar_comando_adb(f"shell input keyevent {keycode}", device_serial)
            time.sleep(0.5)
        elif digit == '+':
            executar_comando_adb("shell input keyevent KEYCODE_PLUS", device_serial)
            time.sleep(0.5)

def verificar_chamada_ativa(device_serial, timeout=15):
    """Aguarda até a chamada ser atendida ou timeout"""
    start = time.time()
    while time.time() - start < timeout:
        try:
            result = subprocess.run([
                ADB_PATH, "-s", device_serial, "shell", "dumpsys", "telephony.registry"
            ], capture_output=True, text=True, timeout=5)
            output = result.stdout

            if "mCallState=2" in output:  # Chamada ativa
                return "ATENDEU"
            elif "mCallState=1" in output:  # Tocando
                time.sleep(1)
                continue
        except Exception as e:
            logging.error(f"Erro ao verificar chamada: {e}")
            return "ERRO"
    return "NAO_ATENDEU"

def discar_e_transferir(numero, nome, data_nascimento, device_serial=None, csv_manager=None):
    """Disca número e tenta transferir via DTMF"""
    try:
        logging.info(f"ADAC - Iniciando discagem: {nome} ({data_nascimento}) - {numero}")
        logging.info(f"ADAC - Número de redirecionamento: {NUMERO_REDIRECIONAMENTO}")

        # Discar usando CALL intent
        success = executar_comando_adb([
            "shell", "am", "start", "-a",
            "android.intent.action.CALL", "-d", f"tel:{numero}"
        ], device_serial)
        
        if not success:
            logging.error("ADAC - ❌ Falha ao iniciar discagem")
            if csv_manager:
                csv_manager.marcar_como_processado(numero, "FALHA_DISCAGEM", nome, data_nascimento)
            return "FALHA_DISCAGEM"

        # Aguardar atendimento
        status_chamada = verificar_chamada_ativa(device_serial, timeout=15)

        if status_chamada == "ATENDEU":
            logging.info("ADAC - ✅ Chamada atendida! Iniciando transferência...")
            enviar_dtmf(NUMERO_REDIRECIONAMENTO, device_serial)
            time.sleep(TEMPO_TRANSFERENCIA)
            logging.info(f"ADAC - ✅ {nome} ({data_nascimento}) - {numero} transferido para {NUMERO_REDIRECIONAMENTO}")

            if csv_manager:
                csv_manager.marcar_como_processado(numero, "ATENDEU", nome, data_nascimento)

        elif status_chamada == "NAO_ATENDEU":
            logging.info(f"ADAC - ❌ {nome} ({data_nascimento}) - {numero} - NÃO ATENDEU")
            if csv_manager:
                csv_manager.marcar_como_processado(numero, "NAO_ATENDEU", nome, data_nascimento)

        # Encerra a chamada
        executar_comando_adb("shell input keyevent KEYCODE_ENDCALL", device_serial)
        time.sleep(2)
        executar_comando_adb("shell input keyevent KEYCODE_HOME", device_serial)

        return status_chamada

    except Exception as e:
        logging.error(f"ADAC - 💥 Erro no processo: {e}")
        executar_comando_adb("shell input keyevent KEYCODE_ENDCALL", device_serial)
        executar_comando_adb("shell input keyevent KEYCODE_HOME", device_serial)
        if csv_manager:
            csv_manager.marcar_como_processado(numero, "ERRO", nome, data_nascimento)
        return "ERRO"