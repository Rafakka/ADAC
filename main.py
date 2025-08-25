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
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('adac_log.txt', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

def verificar_adb():
    """Verifica se o ADB está funcionando"""
    try:
        result = subprocess.run([ADB_PATH, "version"], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            logging.error("ADB não está funcionando corretamente")
            return False
        logging.info(f"ADB encontrado: {result.stdout.splitlines()[0]}")
        return True
    except Exception as e:
        logging.error(f"Erro ao verificar ADB: {e}")
        return False

def detectar_dispositivos():
    """Detecta dispositivos Android conectados"""
    try:
        result = subprocess.run([ADB_PATH, "devices", "-l"], capture_output=True, text=True, timeout=30)
        devices = []
        
        for line in result.stdout.splitlines():
            if "device usb:" in line:
                device_id = line.split()[0]
                devices.append(device_id)
                logging.info(f"Dispositivo detectado: {line}")
        
        return devices if devices else None
        
    except Exception as e:
        logging.error(f"Erro ao detectar dispositivos: {e}")
        return None

def main():
    logging.info("=== ADAC - Auto Discador iniciado ===")
    
    # Verificar ADB
    if not verificar_adb():
        logging.error("ADB não disponível.")
        sys.exit(1)
    
    # Detectar dispositivos
    devices = detectar_dispositivos()
    if not devices:
        logging.error("Nenhum celular detectado.")
        sys.exit(1)

    CELULAR = devices[0]
    logging.info(f"Usando celular: {CELULAR}")

    # Obter caminho do CSV
    if len(sys.argv) < 2:
        csv_path = input("Digite o caminho do CSV: ").strip()
    else:
        csv_path = sys.argv[1].strip()

    # Inicializar gerenciador CSV
    try:
        csv_manager = CSVManager([csv_path])
        csv_manager.criar_csv_inicial()
        
        contatos = csv_manager.ler_contatos()
        logging.info(f"Encontrados {len(contatos)} contatos para discar")

        if not contatos:
            logging.info("Nenhum contato para processar.")
            sys.exit(0)

        # Processar cada contato
        for i, contato in enumerate(contatos, 1):
            numero = contato["numero"]
            nome = contato.get("nome", "Não informado")
            data_nascimento = contato.get("data_nascimento", "Não informada")
            
            logging.info(f"[{i}/{len(contatos)}] Processando: {nome}")
            
            try:
                resultado = discar_e_transferir(
                    numero, 
                    nome, 
                    data_nascimento, 
                    CELULAR, 
                    csv_manager
                )
                
                # Log final baseado no resultado
                if resultado == "ATENDEU":
                    logging.info(f"ADAC - ✅ {nome} ({data_nascimento}) - {numero} - ATENDEU, registro feito por ADAC")
                elif resultado == "NAO_ATENDEU":
                    logging.info(f"ADAC - ❌ {nome} ({data_nascimento}) - {numero} - NÃO ATENDEU, registro feito por ADAC")
                
                # Pausa entre chamadas
                time.sleep(3)
                
            except Exception as e:
                logging.error(f"Erro ao processar {numero}: {e}")
                csv_manager.marcar_como_processado(numero, "ERRO", nome, data_nascimento)
                continue

        logging.info("=== ADAC - Processamento concluído ===")

    except Exception as e:
        logging.error(f"Erro no processamento: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()