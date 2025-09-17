import subprocess
import os
import logging

ADB_PATH = "adb"  # ou caminho absoluto se precisar

def executar_comando_adb(comando, device_serial=None):
    """Executa comando ADB"""
    try:
        cmd = [ADB_PATH]
        if device_serial:
            cmd.extend(["-s", device_serial])
        
        if isinstance(comando, str):
            cmd.extend(comando.split())
        else:
            cmd.extend(comando)
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode != 0:
            logging.error(f"Erro no ADB: {result.stderr}")
            return False
        return True
    except Exception as e:
        logging.error(f"Exceção: {e}")
        return False

def enviar_sms(numero, mensagem, device_serial=None):
    """
    Envia SMS para o número informado usando ADB.
    Necessário que o aparelho permita o uso do comando 'service call isms'.
    """
    try:
        logging.info(f"📩 Enviando SMS para {numero}: {mensagem}")
        
        comando = [
            "shell",
            "service", "call", "isms", "7",
            "i32", "0",  # subscription (0 se 1 chip, 1 se dual sim)
            "s16", "com.android.mms.service",  # pacote que envia SMS
            "s16", numero,
            "s16", "null",
            "s16", mensagem,
            "s16", "null",
            "s16", "null"
        ]
        
        if executar_comando_adb(comando, device_serial):
            logging.info("✅ SMS enviado com sucesso")
            return True
        else:
            logging.error("❌ Falha ao enviar SMS")
            return False
    except Exception as e:
        logging.error(f"Erro ao enviar SMS: {e}")
        return False


if __name__ == "__main__":
    numero_teste = "11998213035"
    mensagem_teste = "RAFA - Teste de SMS via ADAC"
    
    ok = enviar_sms(numero_teste, mensagem_teste)
    print("SMS enviado?", ok)
