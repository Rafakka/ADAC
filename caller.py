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
    except Exception as e:
        logging.error(f"Exceção ao executar comando ADB: {e}")
        return False

def discar_e_transferir(numero, device_serial=None):
    """Disca número usando CALL intent (funciona no seu Motorola!)"""
    try:
        logging.info(f"📞 Discando para {numero}...")
        
        # 1. Usar o comando que FUNCIONA: CALL intent
        success = executar_comando_adb(
            f"shell am start -a android.intent.action.CALL -d tel:{numero}", 
            device_serial
        )
        
        if not success:
            logging.error("❌ Falha ao iniciar discagem")
            return False
        
        # 2. Aguardar discagem completa
        logging.info(f"⏳ Aguardando {TEMPO_DISCAGEM}s para discagem...")
        time.sleep(TEMPO_DISCAGEM)
        
        # 3. Verificar se a chamada está ativa
        result = subprocess.run([
            ADB_PATH, "-s", device_serial, "shell", "dumpsys", "telephony.registry"
        ], capture_output=True, text=True, timeout=10)
        
        if "mCallState=2" not in result.stdout:
            logging.warning("⚠️ Chamada não está ativa, verificando...")
            # Tentar verificar novamente
            time.sleep(3)
            result = subprocess.run([
                ADB_PATH, "-s", device_serial, "shell", "dumpsys", "telephony.registry"
            ], capture_output=True, text=True, timeout=10)
            
            if "mCallState=2" not in result.stdout:
                logging.error("❌ Chamada não foi estabelecida")
                executar_comando_adb("shell input keyevent KEYCODE_ENDCALL", device_serial)
                return False
        
        logging.info("✅ Chamada estabelecida com sucesso!")
        
        # 4. Transferir chamada
        logging.info("🔄 Transferindo chamada...")
        executar_comando_adb("shell input keyevent KEYCODE_CALL", device_serial)
        
        time.sleep(TEMPO_TRANSFERENCIA)
        
        # 5. Encerrar chamada
        logging.info("📴 Encerrando chamada...")
        executar_comando_adb("shell input keyevent KEYCODE_ENDCALL", device_serial)
        time.sleep(2)
        
        # 6. Voltar para home (funciona no seu Motorola)
        executar_comando_adb("shell input keyevent KEYCODE_HOME", device_serial)
        
        logging.info("🎯 Discagem e transferência concluídas com sucesso!")
        return True
        
    except Exception as e:
        logging.error(f"💥 Erro no processo de discagem: {e}")
        # Limpeza em caso de erro
        executar_comando_adb("shell input keyevent KEYCODE_ENDCALL", device_serial)
        executar_comando_adb("shell input keyevent KEYCODE_HOME", device_serial)
        return False