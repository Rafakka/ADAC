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



def verificar_adb():
    """Verifica se o ADB está funcionando corretamente"""
    try:
        result = subprocess.run([ADB_PATH, "version"], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            logging.error("ADB não está funcionando corretamente")
            return False
        return True
    except subprocess.TimeoutExpired:
        logging.error("Timeout ao verificar ADB")
        return False
    except Exception as e:
        logging.error(f"Erro ao verificar ADB: {e}")
        return False

def detectar_dispositivos():
    """Detecta dispositivos Android conectados"""
    try:
        result = subprocess.run([ADB_PATH, "devices"], capture_output=True, text=True, timeout=30)
        devices = [line.split()[0] for line in result.stdout.splitlines() if "\tdevice" in line]
        
        if not devices:
            logging.warning("Nenhum dispositivo detectado. Verifique:")
            logging.warning("1. Depuração USB está habilitada")
            logging.warning("2. Cable USB está conectado")
            logging.warning("3. Autorizou o computador no dispositivo")
            return None
        
        return devices
    except subprocess.TimeoutExpired:
        logging.error("Timeout ao detectar dispositivos")
        return None
    except Exception as e:
        logging.error(f"Erro ao detectar dispositivos: {e}")
        return None

def main():
    logging.info("Iniciando Auto Discador")
    
    # Verificar se ADB está funcionando
    if not verificar_adb():
        logging.error("ADB não está disponível. Verifique a instalação.")
        sys.exit(1)
    
    # Detectar dispositivos
    devices = detectar_dispositivos()
    if not devices:
        logging.error("Nenhum celular detectado. Conecte o celular e habilite a depuração USB.")
        sys.exit(1)

    CELULAR = devices[0]
    logging.info(f"Usando celular: {CELULAR}")

    # Obter caminho do CSV
    if len(sys.argv) < 2:
        csv_path = input("Digite o caminho do CSV (ex: /app/contatos/contatos.csv): ").strip()
    else:
        csv_path = sys.argv[1].strip()

    # Inicializar gerenciador CSV
    try:
        csv_manager = CSVManager([csv_path])
        csv_manager.criar_csv_inicial()
        
        contatos = csv_manager.ler_contatos()
        logging.info(f"Encontrados {len(contatos)} contatos para discar")

        # Processar cada contato
        for i, contato in enumerate(contatos, 1):
            numero = contato["numero"]
            logging.info(f"[{i}/{len(contatos)}] Discando {numero}...")
            
            try:
                success = discar_e_transferir(numero, CELULAR)
                if success:
                    logging.info(f"Chamada para {numero} realizada com sucesso")
                    # Marcar como processado no CSV
                    csv_manager.marcar_como_processado(numero, "SUCESSO")
                else:
                    logging.error(f"Falha ao discar para {numero}")
                    csv_manager.marcar_como_processado(numero, "FALHA")
                
                # Pequena pausa entre chamadas
                time.sleep(2)
                
            except Exception as e:
                logging.error(f"Erro ao processar {numero}: {e}")
                csv_manager.marcar_como_processado(numero, "ERRO")
                continue

        logging.info("Processamento de todos os contatos concluído")

    except Exception as e:
        logging.error(f"Erro no processamento: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()