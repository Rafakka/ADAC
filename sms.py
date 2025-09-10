import logging
import time
import subprocess
from config import ADB_PATH

def enviar_sms(numero, nome, device_serial=None):
    """
    Envia SMS automático para o número informado
    com mensagem personalizada e link do WhatsApp
    """
    try:
        logging.info(f"📱 Preparando para enviar SMS para: {numero} - {nome}")
        
        # Mensagem personalizada com link do WhatsApp
        mensagem = f"Olá {nome}! Tentei entrar em contato. Podemos conversar pelo WhatsApp? wa.me/5511999999999"
        
        # Comando ADB para abrir o app de SMS
        success = executar_comando_adb_sms([
            "shell", "am", "start",
            "-a", "android.intent.action.SENDTO",
            "-d", f"sms:{numero}",
            "--es", "sms_body", mensagem
        ], device_serial)
        
        if not success:
            logging.error("❌ Falha ao abrir app de SMS")
            return False
        
        # Aguardar app abrir
        time.sleep(3)
        
        # Clicar para enviar SMS (simular Enter)
        executar_comando_adb_sms("shell input keyevent KEYCODE_ENTER", device_serial)
        time.sleep(2)
        
        # Confirmar envio (depende do app de SMS)
        executar_comando_adb_sms("shell input keyevent KEYCODE_ENTER", device_serial)
        
        logging.info(f"✅ SMS enviado com sucesso para: {numero}")
        return True
        
    except Exception as e:
        logging.error(f"❌ Erro ao enviar SMS: {e}")
        return False

def executar_comando_adb_sms(comando, device_serial=None):
    """Executa comando ADB específico para SMS"""
    try:
        cmd = [ADB_PATH]
        if device_serial:
            cmd.extend(['-s', device_serial])
        
        if isinstance(comando, str):
            cmd.extend(comando.split())
        else:
            cmd.extend(comando)
        
        startupinfo = None
        import os
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
        
        return result.returncode == 0
        
    except Exception as e:
        logging.error(f"Erro no comando ADB SMS: {e}")
        return False

def obter_numero_whatsapp(device_serial=None):
    """
    Tenta obter o número do WhatsApp instalado no dispositivo
    Retorna o número formatado ou None se não conseguir
    """
    try:
        # Tentar obter informações da conta do WhatsApp
        result = subprocess.run([
            ADB_PATH, "-s", device_serial if device_serial else "",
            "shell", "dumpsys", "account", "|", "grep", "WhatsApp"
        ], capture_output=True, text=True, timeout=10)
        
        output = result.stdout
        
        # Procurar padrões de número telefônico
        import re
        numeros = re.findall(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', output)
        
        if numeros:
            numero_whatsapp = numeros[0].replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
            logging.info(f"📞 Número do WhatsApp detectado: {numero_whatsapp}")
            return numero_whatsapp
        
        return None
        
    except Exception as e:
        logging.error(f"Erro ao obter número do WhatsApp: {e}")
        return None