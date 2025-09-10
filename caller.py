import subprocess
import time
import logging
import os
from config import ADB_PATH, SMS_ENABLED, SMS_MENSAGEM, TEMPO_TRANSFERENCIA, NUMERO_REDIRECIONAMENTO, TENTATIVAS_REDISCAGEM, WHATSAPP_NUMBER

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

def transferir_ligacao(device_serial):
    """Transfere a ligação para o número configurado"""
    try:
        logging.info(f"🔄 Transferindo para: {NUMERO_REDIRECIONAMENTO}")
        
        # 1. Abrir teclado numérico durante a chamada
        executar_comando_adb("shell input keyevent KEYCODE_CALL", device_serial)
        time.sleep(1)
        
        # 2. Digitar o número de redirecionamento
        for digit in NUMERO_REDIRECIONAMENTO:
            executar_comando_adb(f"shell input text {digit}", device_serial)
            time.sleep(0.1)
        
        time.sleep(1)
        
        # 3. Confirmar a transferência (tecla de chamada novamente)
        executar_comando_adb("shell input keyevent KEYCODE_CALL", device_serial)
        
        logging.info("✅ Transferência realizada")
        return True
        
    except Exception as e:
        logging.error(f"❌ Erro na transferência: {e}")
        return False

def verificar_chamada_ativa(device_serial):
    """Verifica se a chamada está ativa e se alguém atendeu"""
    try:
        result = subprocess.run([
            ADB_PATH, "-s", device_serial, "shell", "dumpsys", "telephony.registry"
        ], capture_output=True, text=True, timeout=10)
        
        output = result.stdout
        
        # Verificar se está ocupado
        if "mCallState=3" in output or "BUSY" in output.upper():
            return "OCUPADO"
        
        # Verificar estados de chamada
        if "mCallState=2" in output:  # Chamada ativa (RINGING ou ACTIVE)
            if "RINGING" in output.upper():
                return "TOCANDO"
            else:
                return "ATIVA"  # Chamada em andamento (alguém atendeu)
        elif "mCallState=1" in output:  # Chamada tocando
            return "TOCANDO"
        elif "mCallState=0" in output:  # Sem chamada
            return "DESLIGADA"
        
        return "INDEFINIDO"
        
    except Exception as e:
        logging.error(f"Erro ao verificar chamada: {e}")
        return "ERRO"
    
def aguardar_desligamento(device_serial, timeout=300):
    """Aguarda até que a chamada seja desligada"""
    try:
        logging.info("⏳ Aguardando desligamento da chamada...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = verificar_chamada_ativa(device_serial)
            
            if status in ["DESLIGADA", "INDEFINIDO", "ERRO"]:
                logging.info("✅ Chamada desligada")
                return True
            elif status == "OCUPADO":
                logging.info("❌ Linha ocupada detectada durante chamada")
                return False
            
            time.sleep(2)
        
        logging.warning("⚠️  Timeout aguardando desligamento")
        return False
        
    except Exception as e:
        logging.error(f"Erro ao aguardar desligamento: {e}")
        return False

def discar_e_transferir(numero, nome, data_nascimento, device_serial=None, csv_manager=None):
    """Disca número e transfere para o número configurado com tentativas"""
    try:
        logging.info(f"ADAC - Iniciando discagem: {nome} ({data_nascimento}) - {numero}")
        logging.info(f"ADAC - Número de redirecionamento: {NUMERO_REDIRECIONAMENTO}")
        
        tentativas = 0
        status_final = "NAO_ATENDEU"
        linha_ocupada = False
        
        while tentativas < TENTATIVAS_REDISCAGEM:
            tentativas += 1
            logging.info(f"ADAC - Tentativa {tentativas} de {TENTATIVAS_REDISCAGEM}")
            
            # Usar CALL intent
            success = executar_comando_adb([
                "shell", "am", "start", "-a", 
                "android.intent.action.CALL", "-d", f"tel:{numero}"
            ], device_serial)
            
            if not success:
                logging.error("ADAC - ❌ Falha ao iniciar discagem")
                status_final = "FALHA_DISCAGEM"
                continue
            
            # Aguardar e verificar status da chamada
            time.sleep(5)
            status_chamada = verificar_chamada_ativa(device_serial)
            
            if status_chamada == "OCUPADO":
                logging.info("ADAC - 📞 Linha ocupada, tentando novamente em 5 segundos...")
                executar_comando_adb("shell input keyevent KEYCODE_ENDCALL", device_serial)
                time.sleep(5)
                linha_ocupada = True
                continue
            
            elif status_chamada == "ATIVA":
                logging.info("ADAC - ✅ Chamada atendida! Transferindo...")
                
                # Transferir para o número configurado
                transferir_ligacao(device_serial)
                time.sleep(2)
                
                # Aguardar até a pessoa desligar
                if aguardar_desligamento(device_serial):
                    logging.info(f"ADAC - ✅ {nome} ({data_nascimento}) - {numero} - ATENDEU, transferido para {NUMERO_REDIRECIONAMENTO}, registro feito por ADAC")
                    status_final = "ATENDEU"
                    break
                else:
                    logging.info("ADAC - ❌ Problema durante a chamada transferida")
                    status_final = "ERRO_TRANSFERENCIA"
            
            elif status_chamada == "TOCANDO":
                logging.info("ADAC - 🔔 Chamada tocando, aguardando...")
                
                # Aguardar até 30 segundos para atender
                for _ in range(15):
                    time.sleep(2)
                    status_chamada = verificar_chamada_ativa(device_serial)
                    
                    if status_chamada == "ATIVA":
                        logging.info("ADAC - ✅ Chamada atendida após espera! Transferindo...")
                        transferir_ligacao(device_serial)
                        time.sleep(2)
                        
                        # Aguardar até a pessoa desligar
                        if aguardar_desligamento(device_serial):
                            logging.info(f"ADAC - ✅ {nome} ({data_nascimento}) - {numero} - ATENDEU, transferido para {NUMERO_REDIRECIONAMENTO}, registro feito por ADAC")
                            status_final = "ATENDEU"
                            break
                        else:
                            logging.info("ADAC - ❌ Problema durante a chamada transferida")
                            status_final = "ERRO_TRANSFERENCIA"
                        break
                    
                    elif status_chamada in ["DESLIGADA", "OCUPADO"]:
                        break
                
                if status_chamada != "ATIVA":
                    logging.info("ADAC - ❌ Chamada não atendida")
                    status_final = "NAO_ATENDEU"
            
            elif status_chamada == "DESLIGADA":
                logging.info("ADAC - ❌ Chamada desligada imediatamente")
                status_final = "NAO_ATENDEU"
            
            # Encerrar chamada antes de próxima tentativa
            executar_comando_adb("shell input keyevent KEYCODE_ENDCALL", device_serial)
            time.sleep(2)
            
            if (status_final == "NAO_ATENDEU" or linha_ocupada) and SMS_ENABLED:
                logging.info("ADAC - 📱 Tentativas esgotadas, enviando SMS...")
            
            # Importar e usar o módulo SMS
            try:
                from sms import enviar_sms, obter_numero_whatsapp
                
                # Obter número do WhatsApp (tentar detectar ou usar configurado)
                numero_whatsapp = obter_numero_whatsapp(device_serial) or WHATSAPP_NUMBER
                
                # Formatar mensagem
                mensagem_final = SMS_MENSAGEM.format(numero_whatsapp)
                
                # Enviar SMS
                if enviar_sms(numero, nome, device_serial):
                    logging.info(f"ADAC - ✅ SMS enviado para {numero}")
                    status_final = "SMS_ENVIADO"
                else:
                    logging.warning("ADAC - ❌ Falha ao enviar SMS")
                    
            except ImportError:
                logging.error("ADAC - ❌ Módulo SMS não encontrado")
            except Exception as e:
                logging.error(f"ADAC - ❌ Erro ao enviar SMS: {e}")

        # Limpar estado final
        executar_comando_adb("shell input keyevent KEYCODE_ENDCALL", device_serial)
        time.sleep(2)
        executar_comando_adb("shell input keyevent KEYCODE_HOME", device_serial)
        
        # Registrar no CSV
        if csv_manager:
            csv_manager.marcar_como_processado(numero, status_final, nome, data_nascimento)
        
        return status_final
        
    except Exception as e:
        logging.error(f"ADAC - 💥 Erro no processo: {e}")
        executar_comando_adb("shell input keyevent KEYCODE_ENDCALL", device_serial)
        executar_comando_adb("shell input keyevent KEYCODE_HOME", device_serial)
        
        if csv_manager:
            csv_manager.marcar_como_processado(numero, "ERRO", nome, data_nascimento)
        
        return "ERRO"
