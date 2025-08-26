import subprocess
import sys
import time
import logging
import os
from csv_manager import CSVManager
from caller import discar_e_transferir
from config import ADB_PATH, CONTATOS_DIR, LOGS_DIR, CSV_DEFAULT_PATH, GUI_ENABLED

if GUI_ENABLED:
    try:
        from gui_integrada import init_gui, log_message, update_gui_status, is_gui_paused, should_stop
        GUI_AVAILABLE = True
    except ImportError as e:
        print(f"GUI não disponível: {e}")
        GUI_AVAILABLE = False
else:
    GUI_AVAILABLE = False


# Configuração de logging tradicional
log_file = os.path.join(LOGS_DIR, 'adac_log.txt')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

def log_combined(message, level="info"):
    """Log para ambos GUI e console"""
    if GUI_AVAILABLE:
        log_message(message, level)
    
    # Log tradicional
    if level == "error":
        logging.error(message)
    elif level == "warning":
        logging.warning(message)
    else:
        logging.info(message)

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
    # Inicializar GUI se disponível
    gui = None
    if GUI_AVAILABLE:
        gui = init_gui()
        if gui:
            # Executar GUI em thread separada
            import threading
            gui_thread = threading.Thread(target=gui.run)
            gui_thread.daemon = True
            gui_thread.start()
            time.sleep(0.5)  # Dar tempo para GUI inicializar

    try:
        log_combined("=== ADAC - Auto Discador iniciado ===")
        log_combined(f"📁 Pasta de contatos: {CONTATOS_DIR}")
        log_combined(f"📁 Pasta de logs: {LOGS_DIR}")
        
        if GUI_AVAILABLE and gui:
            update_gui_status(status="Inicializando...")

        # Verificar ADB
        if not verificar_adb():
            log_combined("ADB não disponível.", "error")
            if GUI_AVAILABLE:
                update_gui_status(status="Erro - ADB não disponível")
            sys.exit(1)

        # Detectar dispositivos
        devices = detectar_dispositivos()
        if not devices:
            log_combined("Nenhum celular detectado.", "error")
            if GUI_AVAILABLE:
                update_gui_status(status="Erro - Nenhum dispositivo")
            sys.exit(1)

        CELULAR = devices[0]
        log_combined(f"Usando celular: {CELULAR}", "success")
        
        if GUI_AVAILABLE:
            update_gui_status(device=f"Conectado: {CELULAR}")

        # Encontrar arquivo CSV
        csv_path = encontrar_arquivo_csv()
        log_combined(f"📋 Usando arquivo CSV: {csv_path}")
        
        if GUI_AVAILABLE:
            update_gui_status(csv=f"Carregado: {os.path.basename(csv_path)}")

        # Inicializar gerenciador CSV
        try:
            csv_manager = CSVManager([csv_path])
            csv_manager.criar_csv_inicial()
            
            contatos = csv_manager.ler_contatos()
            total_contatos = len(contatos)
            log_combined(f"Encontrados {total_contatos} contatos para discar", "success")
            
            if GUI_AVAILABLE:
                update_gui_status(
                    total=total_contatos,
                    status="Pronto para discagem"
                )

            if not contatos:
                log_combined("Nenhum contato para processar. Adicione números no CSV.", "warning")
                sys.exit(0)

            # Processar cada contato
            sucesso_count = 0
            falha_count = 0
            
            for i, contato in enumerate(contatos, 1):
                # Verificar se deve pausar ou parar
                if GUI_AVAILABLE:
                    while is_gui_paused() and not should_stop():
                        time.sleep(0.5)
                    
                    if should_stop():
                        log_combined("Execução interrompida pelo usuário", "warning")
                        break
                
                numero = contato["numero"]
                nome = contato.get("nome", "Não informado")
                data_nascimento = contato.get("data_nascimento", "Não informada")
                
                log_combined(f"[{i}/{total_contatos}] Processando: {nome}")
                
                if GUI_AVAILABLE:
                    update_gui_status(
                        processados=i-1,
                        sucesso=sucesso_count,
                        falha=falha_count,
                        current=f"{nome} - {numero}",
                        status="Discando..."
                    )
                
                try:
                    resultado = discar_e_transferir(
                        numero, 
                        nome, 
                        data_nascimento, 
                        CELULAR, 
                        csv_manager
                    )
                    
                    # Atualizar contadores
                    if resultado == "ATENDEU":
                        sucesso_count += 1
                        log_combined(f"✅ {nome} ({data_nascimento}) - {numero} - ATENDEU, registro feito por ADAC", "success")
                    elif resultado == "NAO_ATENDEU":
                        falha_count += 1
                        log_combined(f"❌ {nome} ({data_nascimento}) - {numero} - NÃO ATENDEU, registro feito por ADAC", "warning")
                    
                    # Atualizar GUI
                    if GUI_AVAILABLE:
                        update_gui_status(
                            processados=i,
                            sucesso=sucesso_count,
                            falha=falha_count
                        )
                    
                    # Pausa entre chamadas
                    time.sleep(3)
                    
                except Exception as e:
                    falha_count += 1
                    log_combined(f"Erro ao processar {numero}: {e}", "error")
                    csv_manager.marcar_como_processado(numero, "ERRO", nome, data_nascimento)
                    
                    if GUI_AVAILABLE:
                        update_gui_status(
                            processados=i,
                            falha=falha_count
                        )
                    continue

            # Relatório final
            log_combined(f"=== ADAC - Processamento concluído ===", "success")
            log_combined(f"📊 Total: {total_contatos} contatos", "success")
            log_combined(f"✅ Sucesso: {sucesso_count}", "success")
            log_combined(f"❌ Falha: {falha_count}", "warning" if falha_count > 0 else "success")
            log_combined(f"📄 Log salvo em: {log_file}")
            
            if GUI_AVAILABLE:
                update_gui_status(
                    status="Concluído",
                    processados=total_contatos,
                    sucesso=sucesso_count,
                    falha=falha_count,
                    current="Processamento finalizado"
                )

        except Exception as e:
            log_combined(f"Erro no processamento: {e}", "error")
            if GUI_AVAILABLE:
                update_gui_status(status=f"Erro: {str(e)}")
            sys.exit(1)

    except KeyboardInterrupt:
        log_combined("Execução interrompida pelo usuário", "warning")
        if GUI_AVAILABLE:
            update_gui_status(status="Interrompido pelo usuário")
    except Exception as e:
        log_combined(f"Erro fatal: {e}", "error")
        if GUI_AVAILABLE:
            update_gui_status(status=f"Erro fatal: {str(e)}")
        sys.exit(1)
    
    # Manter GUI aberta por alguns segundos
    if GUI_AVAILABLE and gui:
        time.sleep(5)

if __name__ == "__main__":
    main()