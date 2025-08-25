import subprocess
import time
import logging
import os
from config import ADB_PATH, TEMPO_DISCAGEM, TEMPO_TRANSFERENCIA
from csv_manager import CSVManager

def executar_comando_adb(comando, device_serial=None):
    """Executa comando ADB com tratamento de erro"""
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
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=30,
            startupinfo=startupinfo
        )
        
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

def verificar_chamada_ativa(device_serial):
    """Verifica se a chamada está ativa e se alguém atendeu"""
    try:
        result = subprocess.run([
            ADB_PATH, "-s", device_serial, "shell", "dumpsys", "telephony.registry"
        ], capture_output=True, text=True, timeout=10)
        
        output = result.stdout
        
        # Verificar estado da chamada
        if "mCallState=2" in output:  # Chamada ativa
            # Verificar se alguém atendeu (estado RINGING -> ACTIVE)
            if "mCallState=1" in output:  # Chamada tocando
                return "TOCANDO"
            elif "mCallState=2" in output:  # Chamada ativa (alguém atendeu)
                return "ATENDEU"
        elif "mCallState=0" in output:  # Sem chamada
            return "NAO_ATENDEU"
        
        return "INDEFINIDO"
        
    except Exception as e:
        logging.error(f"Erro ao verificar chamada: {e}")
        return "ERRO"

def discar_e_transferir(numero, nome, data_nascimento, device_serial=None, csv_manager=None):
    """Disca número e retorna status detalhado"""
    try:
        # Log inicial formatado
        logging.info(f"ADAC - Iniciando discagem: {nome} ({data_nascimento}) - {numero}")
        
        # Usar CALL intent
        success = executar_comando_adb([
            "shell", "am", "start", "-a", 
            "android.intent.action.CALL", "-d", f"tel:{numero}"
        ], device_serial)
        
        if not success:
            logging.error("ADAC - ❌ Falha ao iniciar discagem")
            if csv_manager:
                csv_manager.marcar_como_processado(numero, "FALHA_DISCAGEM", nome, data_nascimento)
            return "FALHA_DISCAGEM"
        
        # Aguardar e verificar status da chamada
        time.sleep(3)
        status_chamada = verificar_chamada_ativa(device_serial)
        
        if status_chamada == "ATENDEU":
            logging.info("ADAC - ✅ Chamada atendida! Transferindo...")
            
            # Transferir chamada
            executar_comando_adb("shell input keyevent KEYCODE_CALL", device_serial)
            time.sleep(TEMPO_TRANSFERENCIA)
            
            # Log de sucesso
            logging.info(f"ADAC - ✅ {nome} ({data_nascimento}) - {numero} - ATENDEU, registro feito por ADAC")
            
            if csv_manager:
                csv_manager.marcar_como_processado(numero, "ATENDEU", nome, data_nascimento)
            
        elif status_chamada == "NAO_ATENDEU":
            logging.info("ADAC - ❌ Chamada não atendida")
            logging.info(f"ADAC - ❌ {nome} ({data_nascimento}) - {numero} - NÃO ATENDEU, registro feito por ADAC")
            
            if csv_manager:
                csv_manager.marcar_como_processado(numero, "NAO_ATENDEU", nome, data_nascimento)
                
        elif status_chamada == "TOCANDO":
            # Aguardar mais tempo se estiver tocando
            time.sleep(10)
            status_chamada = verificar_chamada_ativa(device_serial)
            
            if status_chamada == "ATENDEU":
                logging.info("ADAC - ✅ Chamada atendida após espera! Transferindo...")
                executar_comando_adb("shell input keyevent KEYCODE_CALL", device_serial)
                time.sleep(TEMPO_TRANSFERENCIA)
                logging.info(f"ADAC - ✅ {nome} ({data_nascimento}) - {numero} - ATENDEU, registro feito por ADAC")
                
                if csv_manager:
                    csv_manager.marcar_como_processado(numero, "ATENDEU", nome, data_nascimento)
            else:
                logging.info(f"ADAC - ❌ {nome} ({data_nascimento}) - {numero} - NÃO ATENDEU, registro feito por ADAC")
                
                if csv_manager:
                    csv_manager.marcar_como_processado(numero, "NAO_ATENDEU", nome, data_nascimento)
        
        # Encerrar chamada independente do resultado
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