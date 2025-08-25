import subprocess
import sys
import time
import logging
import os
from csv_manager import CSVManager
from caller import discar_e_transferir
from config import ADB_PATH, CONTATOS_DIR, LOGS_DIR, CSV_DEFAULT_PATH

# Configuração de logging
log_file = os.path.join(LOGS_DIR, 'adac_log.txt')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

try:
    from gui_manager import ADACGUI
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

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

def encontrar_arquivo_csv():
    """Encontra automaticamente o arquivo CSV na pasta contatos/"""
    try:
        # Verificar se existe o arquivo padrão
        if os.path.exists(CSV_DEFAULT_PATH):
            return CSV_DEFAULT_PATH
        
        # Procurar por qualquer arquivo CSV na pasta
        for arquivo in os.listdir(CONTATOS_DIR):
            if arquivo.lower().endswith('.csv'):
                return os.path.join(CONTATOS_DIR, arquivo)
        
        # Se não encontrou, criar um novo
        logging.info("Nenhum arquivo CSV encontrado. Criando novo arquivo...")
        return CSV_DEFAULT_PATH
        
    except Exception as e:
        logging.error(f"Erro ao procurar arquivo CSV: {e}")
        return CSV_DEFAULT_PATH

def main():

    use_gui = False
    if GUI_AVAILABLE and "--gui" in sys.argv:
        use_gui = True

    if use_gui:
        gui = ADACGUI()
        gui.log_message("Iniciando ADAC com interface gráfica", "success")
    else:
        logging.info("=== ADAC - Auto Discador iniciado ===")
        logging.info(f"📁 Pasta de contatos: {CONTATOS_DIR}")
        logging.info(f"📁 Pasta de logs: {LOGS_DIR}")
    
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

        # Encontrar arquivo CSV automaticamente
        csv_path = encontrar_arquivo_csv()
        logging.info(f"📋 Usando arquivo CSV: {csv_path}")

        # Inicializar gerenciador CSV
        try:
            csv_manager = CSVManager([csv_path])
            csv_manager.criar_csv_inicial()
            
            contatos = csv_manager.ler_contatos()
            logging.info(f"Encontrados {len(contatos)} contatos para discar")

            if not contatos:
                logging.info("Nenhum contato para processar. Adicione números no CSV.")
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
            logging.info(f"📄 Log salvo em: {log_file}")

        except Exception as e:
            logging.error(f"Erro no processamento: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()