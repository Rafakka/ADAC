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
        
        # Se o comando é uma string, split, se já é lista, usar diretamente
        if isinstance(comando, str):
            cmd.extend(comando.split())
        else:
            cmd.extend(comando)
        
        # Configurar environment para evitar popups de console no Windows
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0  # SW_HIDE
        
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
    except Exception as e:
        logging.error(f"Exceção ao executar comando ADB: {e}")
        return False

def discar_e_transferir(numero, device_serial=None):
    """Disca número usando CALL intent"""
    try:
        logging.info(f"📞 Discando para {numero}...")
        
        # Usar o comando que FUNCIONA: CALL intent
        success = executar_comando_adb([
            "shell", "am", "start", "-a", 
            "android.intent.action.CALL", "-d", f"tel:{numero}"
        ], device_serial)
        
        if not success:
            logging.error("❌ Falha ao iniciar discagem")
            return False
        
        # Aguardar discagem completa
        logging.info(f"⏳ Aguardando {TEMPO_DISCAGEM}s para discagem...")
        time.sleep(TEMPO_DISCAGEM)
        
        # Verificar se a chamada está ativa
        result = subprocess.run([
            ADB_PATH, "-s", device_serial, "shell", "dumpsys", "telephony.registry"
        ], capture_output=True, text=True, timeout=10)
        
        if "mCallState=2" not in result.stdout:
            logging.warning("⚠️ Chamada não está ativa, verificando...")
            time.sleep(3)
            result = subprocess.run([
                ADB_PATH, "-s", device_serial, "shell", "dumpsys", "telephony.registry"
            ], capture_output=True, text=True, timeout=10)
            
            if "mCallState=2" not in result.stdout:
                logging.error("❌ Chamada não foi estabelecida")
                executar_comando_adb("shell input keyevent KEYCODE_ENDCALL", device_serial)
                return False
        
        logging.info("✅ Chamada estabelecida com sucesso!")
        
        # Transferir chamada
        logging.info("🔄 Transferindo chamada...")
        executar_comando_adb("shell input keyevent KEYCODE_CALL", device_serial)
        
        time.sleep(TEMPO_TRANSFERENCIA)
        
        # Encerrar chamada
        logging.info("📴 Encerrando chamada...")
        executar_comando_adb("shell input keyevent KEYCODE_ENDCALL", device_serial)
        time.sleep(2)
        
        # Voltar para home
        executar_comando_adb("shell input keyevent KEYCODE_HOME", device_serial)
        
        logging.info("🎯 Discagem e transferência concluídas com sucesso!")
        return True
        
    except Exception as e:
        logging.error(f"💥 Erro no processo de discagem: {e}")
        executar_comando_adb("shell input keyevent KEYCODE_ENDCALL", device_serial)
        executar_comando_adb("shell input keyevent KEYCODE_HOME", device_serial)
        return False