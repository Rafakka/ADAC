import subprocess
import sys
import time
import logging
from csv_manager import CSVManager
from caller import discar_e_transferir
from config import ADB_PATH

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('autodialer.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def verificar_adb():
    """Verifica se o ADB está funcionando corretamente"""
    try:
        result = subprocess.run([ADB_PATH, "version"], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            logging.error("ADB não está funcionando corretamente")
            logging.error(f"Erro: {result.stderr}")
            return False
        logging.info(f"ADB encontrado: {result.stdout.splitlines()[0]}")
        return True
    except subprocess.TimeoutExpired:
        logging.error("Timeout ao verificar ADB")
        return False
    except Exception as e:
        logging.error(f"Erro ao verificar ADB: {e}")
        return False

def detectar_dispositivos_com_tentativas():
    """Tenta detectar dispositivos com múltiplas tentativas"""
    for tentativa in range(3):
        try:
            logging.info(f"Tentativa {tentativa + 1} de detectar dispositivos...")
            
            # Reiniciar servidor ADB na primeira tentativa
            if tentativa == 0:
                subprocess.run([ADB_PATH, "kill-server"], capture_output=True)
                subprocess.run([ADB_PATH, "start-server"], capture_output=True)
                time.sleep(2)
            
            result = subprocess.run([ADB_PATH, "devices", "-l"], capture_output=True, text=True, timeout=30)
            devices = []
            
            for line in result.stdout.splitlines():
                if "device usb:" in line:
                    device_id = line.split()[0]
                    devices.append(device_id)
                    logging.info(f"Dispositivo encontrado: {line}")
            
            if devices:
                return devices
            
            logging.warning("Nenhum dispositivo encontrado. Verifique:")
            logging.warning("- Depuração USB habilitada")
            logging.warning("- Cable USB conectado")
            logging.warning("- Autorização concedida no dispositivo")
            
            time.sleep(3)  # Aguardar antes da próxima tentativa
            
        except Exception as e:
            logging.error(f"Erro na tentativa {tentativa + 1}: {e}")
            time.sleep(2)
    
    return None

def testar_dispositivo(device_serial):
    """Testa se o dispositivo está respondendo"""
    try:
        # Testar comando simples
        result = subprocess.run([
            ADB_PATH, "-s", device_serial, "shell", "getprop", "ro.product.model"
        ], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            model = result.stdout.strip()
            logging.info(f"Dispositivo testado: {model}")
            return True
        return False
        
    except Exception as e:
        logging.error(f"Erro ao testar dispositivo: {e}")
        return False

def conectar_via_tcpip(ip="192.168.1.100", porta=5555):
    """Conectar ao dispositivo via TCP/IP"""
    try:
        logging.info(f"🔗 Conectando via TCP/IP: {ip}:{porta}")
        result = subprocess.run([
            ADB_PATH, "connect", f"{ip}:{porta}"
        ], capture_output=True, text=True, timeout=30)
        
        if "connected" in result.stdout:
            logging.info(f"✅ Conectado via TCP/IP: {ip}:{porta}")
            return True
        else:
            logging.error(f"❌ Falha na conexão TCP/IP: {result.stderr}")
            return False
    except Exception as e:
        logging.error(f"Erro na conexão TCP/IP: {e}")
        return False

def main():
    logging.info("Iniciando Auto Discador")
    
    # Verificar se ADB está funcionando
    if not verificar_adb():
        logging.error("ADB não está disponível. Verifique a instalação.")
        sys.exit(1)
    
    # Detectar dispositivos com múltiplas tentativas
    devices = detectar_dispositivos_com_tentativas()
    if not devices:
        logging.error("Nenhum celular detectado após várias tentativas.")
        logging.error("💡 Dica: Tente conectar via TCP/IP ou verifique a conexão USB")
        sys.exit(1)

    CELULAR = devices[0]
    logging.info(f"📱 Usando celular: {CELULAR}")

    # Testar se o dispositivo está respondendo
    if not testar_dispositivo(CELULAR):
        logging.error("❌ Dispositivo não está respondendo aos comandos")
        sys.exit(1)

    # Obter caminho do CSV
    if len(sys.argv) < 2:
        csv_path = input("Digite o caminho do CSV (ex: contatos.csv): ").strip()
    else:
        csv_path = sys.argv[1].strip()

    # Inicializar gerenciador CSV
    try:
        csv_manager = CSVManager([csv_path])
        csv_manager.criar_csv_inicial()
        
        contatos = csv_manager.ler_contatos()
        logging.info(f"📋 Encontrados {len(contatos)} contatos para discar")

        if not contatos:
            logging.info("ℹ️ Nenhum contato para processar. Adicione números no CSV.")
            sys.exit(0)

        # Processar cada contato
        for i, contato in enumerate(contatos, 1):
            numero = contato["numero"]
            logging.info(f"[{i}/{len(contatos)}] 📞 Processando {numero}...")
            
            try:
                success = discar_e_transferir(numero, CELULAR)
                if success:
                    logging.info(f"✅ Chamada para {numero} realizada com sucesso")
                    csv_manager.marcar_como_processado(numero, "SUCESSO")
                else:
                    logging.error(f"❌ Falha ao discar para {numero}")
                    csv_manager.marcar_como_processado(numero, "FALHA")
                
                # Pequena pausa entre chamadas
                time.sleep(3)
                
            except Exception as e:
                logging.error(f"💥 Erro ao processar {numero}: {e}")
                csv_manager.marcar_como_processado(numero, "ERRO")
                continue

        logging.info("🎉 Processamento de todos os contatos concluído")

    except Exception as e:
        logging.error(f"💥 Erro no processamento: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()