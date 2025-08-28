import subprocess
import time
import logging
import os
from config import ADB_PATH, TEMPO_DISCAGEM, TEMPO_TRANSFERENCIA, NUMERO_REDIRECIONAMENTO
from csv_manager import CSVManager

def executar_comando_adb(comando, celular=None, timeout=30):
    """Executa um comando ADB, opcionalmente em um dispositivo específico"""
    try:
        cmd = [ADB_PATH]
        if celular:
            cmd.extend(['-s', celular])

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
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            startupinfo=startupinfo
        )

        if result.returncode != 0:
            logging.error(f"Erro no comando ADB: {result.stderr.strip()}")
            return False

        return True

    except subprocess.TimeoutExpired:
        logging.error("Timeout ao executar comando ADB")
        return False
    except Exception as e:
        logging.exception(f"Exceção ao executar comando ADB: {e}")
        return False


def transferir_ligacao(celular):
    """Transfere a ligação para o número configurado"""
    try:
        logging.info(f"🔄 Transferindo para: {NUMERO_REDIRECIONAMENTO}")

        # Abrir teclado numérico
        executar_comando_adb("shell input keyevent KEYCODE_CALL", celular)
        time.sleep(1)

        # Digitar número de redirecionamento
        for digit in NUMERO_REDIRECIONAMENTO:
            executar_comando_adb(f"shell input text {digit}", celular)
            time.sleep(0.1)

        time.sleep(1)
        # Confirmar transferência
        executar_comando_adb("shell input keyevent KEYCODE_CALL", celular)

        logging.info("✅ Transferência realizada")
        return True

    except Exception as e:
        logging.exception(f"❌ Erro na transferência: {e}")
        return False


def verificar_chamada_ativa(celular):
    """Retorna o status da chamada: TOCANDO, ATENDEU, NAO_ATENDEU ou INDEFINIDO"""
    try:
        result = subprocess.run(
            [ADB_PATH, "-s", celular, "shell", "dumpsys", "telephony.registry"],
            capture_output=True,
            text=True,
            timeout=10
        )

        output = result.stdout
        if "mCallState=1" in output:
            return "TOCANDO"
        elif "mCallState=2" in output:
            return "ATENDEU"
        elif "mCallState=0" in output:
            return "NAO_ATENDEU"
        else:
            return "INDEFINIDO"

    except Exception as e:
        logging.exception(f"Erro ao verificar chamada: {e}")
        return "ERRO"


def discar_e_transferir(numero, nome, data_nascimento, celular, csv_manager: CSVManager):
    """Disca número e transfere a chamada para o número configurado"""
    try:
        logging.info(f"ADAC - Iniciando discagem: {nome} ({data_nascimento}) - {numero}")

        # Discar usando intent
        if not executar_comando_adb([
            "shell", "am", "start", "-a",
            "android.intent.action.CALL", "-d", f"tel:{numero}"
        ], celular):
            logging.error("ADAC - ❌ Falha ao iniciar discagem")
            if csv_manager:
                csv_manager.marcar_como_processado(numero, "FALHA_DISCAGEM", nome, data_nascimento)
            return "FALHA_DISCAGEM"

        # Esperar e verificar status da chamada com loop de checagem
        timeout = TEMPO_DISCAGEM
        interval = 1
        status_chamada = "INDEFINIDO"
        while timeout > 0:
            status_chamada = verificar_chamada_ativa(celular)
            if status_chamada in ["ATENDEU", "NAO_ATENDEU"]:
                break
            time.sleep(interval)
            timeout -= interval

        if status_chamada == "ATENDEU":
            logging.info("ADAC - ✅ Chamada atendida! Transferindo...")
            transferir_ligacao(celular)
            time.sleep(TEMPO_TRANSFERENCIA)
            logging.info(f"ADAC - ✅ {nome} ({data_nascimento}) - {numero} - ATENDEU, transferido para {NUMERO_REDIRECIONAMENTO}")

            if csv_manager:
                csv_manager.marcar_como_processado(numero, "ATENDEU", nome, data_nascimento)

        elif status_chamada == "NAO_ATENDEU":
            logging.info(f"ADAC - ❌ {nome} ({data_nascimento}) - {numero} - NÃO ATENDEU")
            if csv_manager:
                csv_manager.marcar_como_processado(numero, "NAO_ATENDEU", nome, data_nascimento)

        else:
            logging.warning(f"ADAC - Status da chamada indefinido para {numero}")
            if csv_manager:
                csv_manager.marcar_como_processado(numero, "INDEFINIDO", nome, data_nascimento)

        # Encerrar chamada e voltar para home
        executar_comando_adb("shell input keyevent KEYCODE_ENDCALL", celular)
        time.sleep(1)
        executar_comando_adb("shell input keyevent KEYCODE_HOME", celular)

        return status_chamada

    except Exception as e:
        logging.exception(f"ADAC - 💥 Erro no processo de {numero}: {e}")
        executar_comando_adb("shell input keyevent KEYCODE_ENDCALL", celular)
        executar_comando_adb("shell input keyevent KEYCODE_HOME", celular)

        if csv_manager:
            csv_manager.marcar_como_processado(numero, "ERRO", nome, data_nascimento)

        return "ERRO"
