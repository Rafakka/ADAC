import subprocess
import time
import logging
import os
from config import ADB_PATH, TEMPO_DISCAGEM, TEMPO_TRANSFERENCIA, NUMERO_REDIRECIONAMENTO
from csv_manager import CSVManager
from logger import log_combined

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


def discar_e_transferir(numero, nome, data_nascimento, celular, csv_manager: CSVManager, gui=None):
    """
    Disca número até 3 tentativas.
    Se atender → transfere automaticamente.
    Se não atender → marca como NAO_ATENDEU no CSV.
    """
    tentativas = 3
    ultima_resposta = "ERRO"

    for tentativa in range(1, tentativas + 1):
        log_combined(
            f"📞 Tentativa {tentativa}/{tentativas} - Discando: {nome} ({numero})",
            "info", gui
        )

        if gui:
            gui.update_status(current=nome, processados=tentativa)

        try:
            # Discar usando intent do Android
            if not executar_comando_adb([
                "shell", "am", "start", "-a",
                "android.intent.action.CALL", "-d", f"tel:{numero}"
            ], celular):
                log_combined("❌ Falha ao iniciar discagem", "error", gui)
                ultima_resposta = "FALHA_DISCAGEM"
                continue

            # Espera até TEMPO_DISCAGEM segundos pela resposta
            timeout = TEMPO_DISCAGEM
            status_chamada = "INDEFINIDO"
            while timeout > 0:
                status_chamada = verificar_chamada_ativa(celular)
                if status_chamada in ["ATENDEU", "NAO_ATENDEU"]:
                    break
                time.sleep(1)
                timeout -= 1

            # Caso tenha atendido → transferir
            if status_chamada == "ATENDEU":
                log_combined(f"✅ {nome} atendeu, transferindo...", "success", gui)
                transferir_ligacao(celular)
                time.sleep(TEMPO_TRANSFERENCIA)
                ultima_resposta = "ATENDEU"

                if csv_manager:
                    csv_manager.marcar_como_processado(numero, "ATENDEU", nome, data_nascimento)
                break  # não precisa tentar de novo

            elif status_chamada == "NAO_ATENDEU":
                log_combined(f"❌ {nome} não atendeu", "error", gui)
                ultima_resposta = "NAO_ATENDEU"

            else:
                log_combined(f"⚠️ Status indefinido para {nome}: {status_chamada}", "warning", gui)
                ultima_resposta = "INDEFINIDO"

        except Exception as e:
            logging.exception(f"Erro ao discar {numero}: {e}")
            ultima_resposta = "ERRO"

        finally:
            # Encerrar chamada a cada tentativa
            executar_comando_adb("shell input keyevent KEYCODE_ENDCALL", celular)
            time.sleep(1)
            executar_comando_adb("shell input keyevent KEYCODE_HOME", celular)

    # Marca no CSV depois das tentativas
    if csv_manager and ultima_resposta != "ATENDEU":
        csv_manager.marcar_como_processado(numero, ultima_resposta, nome, data_nascimento)

    return ultima_resposta
