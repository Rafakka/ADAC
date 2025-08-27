import subprocess
import sys
import threading
import time as time_module  # Renomear para evitar conflito
import logging
import os
import pygame

os.environ['SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR'] = '0'
os.environ['SDL_VIDEO_X11_SHM'] = '0'  # Desativa shared memory

from csv_manager import CSVManager
from caller import discar_e_transferir
from config import ADB_PATH, CONTATOS_DIR, LOGS_DIR, CSV_DEFAULT_PATH, GUI_ENABLED

# Configuração de GUI - usar variável global
GUI_AVAILABLE = False
if GUI_ENABLED:
    try:
        from gui_integrada import init_gui, log_message, update_gui_status, is_gui_paused, should_stop
        GUI_AVAILABLE = True
    except ImportError as e:
        print(f"GUI não disponível: {e}")
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
    global GUI_AVAILABLE
    if GUI_AVAILABLE:
        log_message(message, level)
    
    if level == "error":
        logging.error(message)
    elif level == "warning":
        logging.warning(message)
    else:
        logging.info(message)

def mostrar_ajuda_erro():
    """Mostra ajuda quando ocorre erro"""
    log_combined("", "warning")
    log_combined("🔧 SOLUÇÃO DE PROBLEMAS:", "header")
    log_combined("1. 📱 Conecte o celular via USB", "warning")
    log_combined("2. ⚙️  Ative a depuração USB (Opções do desenvolvedor)", "warning") 
    log_combined("3. ✅ Autorize o computador no popup do celular", "warning")
    log_combined("4. 🔄 Execute: adb devices para testar", "warning")
    log_combined("5. 🚫 Pressione ESC para cancelar", "warning")
    log_combined("", "warning")

def verificar_adb():
    """Verifica se o ADB está funcionando - NÃO USA sys.exit()"""
    try:
        result = subprocess.run([ADB_PATH, "version"], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            log_combined("ADB não está funcionando corretamente", "error")
            return False
        log_combined(f"ADB encontrado: {result.stdout.splitlines()[0]}", "success")
        return True
    except Exception as e:
        log_combined(f"Erro ao verificar ADB: {e}", "error")
        return False  # Retorna False, não sai do programa

if not verificar_adb():
    log_combined("ADB não disponível.", "error")
    mostrar_ajuda_erro()  # 👈 Mostra ajuda
    if GUI_AVAILABLE:
        update_gui_status(status="Erro - ADB não disponível")
    execution_successful = False

def detectar_dispositivos():
    """Detecta dispositivos Android - NÃO USA sys.exit()"""
    try:
        result = subprocess.run([ADB_PATH, "devices", "-l"], capture_output=True, text=True, timeout=30)
        devices = []
        
        for line in result.stdout.splitlines():
            if "device usb:" in line:
                device_id = line.split()[0]
                devices.append(device_id)
                log_combined(f"Dispositivo detectado: {line}", "success")
        
        return devices if devices else None
        
    except Exception as e:
        log_combined(f"Erro ao detectar dispositivos: {e}", "error")
        return None  # Retorna None, não sai do programa

def encontrar_arquivo_csv():
    """Encontra automaticamente o arquivo CSV na pasta contatos/"""
    try:
        if os.path.exists(CSV_DEFAULT_PATH):
            return CSV_DEFAULT_PATH
        
        for arquivo in os.listdir(CONTATOS_DIR):
            if arquivo.lower().endswith('.csv'):
                return os.path.join(CONTATOS_DIR, arquivo)
        
        log_combined("Nenhum arquivo CSV encontrado. Criando novo arquivo...", "warning")
        return CSV_DEFAULT_PATH
        
    except Exception as e:
        log_combined(f"Erro ao procurar arquivo CSV: {e}", "error")
        return CSV_DEFAULT_PATH
    
def esperar_celular_conectar(gui=None):
    """Aguarda até que um celular seja conectado ou ESC seja pressionado"""
    global GUI_AVAILABLE
    
    log_combined("🔍 Aguardando conexão do celular...", "warning")
    log_combined("💡 Conecte o celular via USB e ative a depuração USB", "warning")
    
    if GUI_AVAILABLE and gui:
        update_gui_status(
            status="Aguardando celular",
            device="Não conectado",
            current="Conecte o celular e ative depuração USB"
        )
    
    # Configurar pygame para detectar ESC
    try:
        import pygame
        clock = pygame.time.Clock()
        waiting = True
        
        while waiting:
            # Verificar se celular foi conectado
            devices = detectar_dispositivos()
            if devices:
                log_combined(f"✅ Celular detectado: {devices[0]}", "success")
                return devices[0]  # Retorna o ID do dispositivo
            
            # Verificar se usuário pressionou ESC
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    log_combined("Operação cancelada pelo usuário", "warning")
                    return None
            
            # Atualizar interface
            if GUI_AVAILABLE and gui and hasattr(gui, 'draw_interface'):
                gui.draw_interface()
            
            # Mensagem de waiting a cada 5 segundos
            if int(time_module.time()) % 5 == 0:
                log_combined("⏳ Aguardando conexão do celular...", "warning")
            
            clock.tick(1)  # Verificar a cada segundo
            
    except Exception as e:
        log_combined(f"Erro ao aguardar celular: {e}", "error")
        return None


def main():
    global GUI_AVAILABLE
    
    # Inicializar GUI se disponível
    gui = None
    gui_thread = None
    
    if GUI_AVAILABLE:
        try:
            gui = init_gui()
            if gui:
                gui_thread = threading.Thread(target=gui.run)
                gui_thread.daemon = True
                gui_thread.start()
                time_module.sleep(1)
                log_combined("Interface gráfica inicializada", "success")
        except Exception as e:
            log_combined(f"Erro ao inicializar GUI: {e}", "error")
            GUI_AVAILABLE = False

    try:
        log_combined("=== ADAC - Auto Discador iniciado ===")
        
        if GUI_AVAILABLE and gui:
            update_gui_status(status="Inicializando...")

        # Verificar ADB primeiro
        if not verificar_adb():
            log_combined("ADB não disponível.", "error")
            mostrar_ajuda_erro()
            if GUI_AVAILABLE:
                update_gui_status(status="Erro - ADB não disponível")
            # Não sair, apenas aguardar na tela final
        else:
            # ADB está OK, agora aguardar celular
            CELULAR = esperar_celular_conectar(gui)
            
            if CELULAR is None:
                log_combined("Operação cancelada pelo usuário", "warning")
                if GUI_AVAILABLE:
                    update_gui_status(status="Cancelado pelo usuário")
            else:
                log_combined(f"✅ Usando celular: {CELULAR}", "success")
                
                if GUI_AVAILABLE:
                    update_gui_status(device=f"Conectado: {CELULAR}")

                # Encontrar arquivo CSV
                csv_path = encontrar_arquivo_csv()
                log_combined(f"📋 Usando arquivo CSV: {csv_path}")
                
                if GUI_AVAILABLE:
                    update_gui_status(csv=f"Carregado: {os.path.basename(csv_path)}")

                # Inicializar gerenciador CSV
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
                else:
                    # Processar cada contato
                    sucesso_count = 0
                    falha_count = 0
                    
                    for i, contato in enumerate(contatos, 1):
                        # Verificar se deve pausar ou parar
                        if GUI_AVAILABLE:
                            while is_gui_paused() and not should_stop():
                                time_module.sleep(0.5)
                            
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
                            
                            if resultado == "ATENDEU":
                                sucesso_count += 1
                                log_combined(f"✅ {nome} ({data_nascimento}) - {numero} - ATENDEU, registro feito por ADAC", "success")
                            elif resultado == "NAO_ATENDEU":
                                falha_count += 1
                                log_combined(f"❌ {nome} ({data_nascimento}) - {numero} - NÃO ATENDEU, registro feito por ADAC", "warning")
                            
                            if GUI_AVAILABLE:
                                update_gui_status(
                                    processados=i,
                                    sucesso=sucesso_count,
                                    falha=falha_count
                                )
                            
                            time_module.sleep(3)
                            
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

    except KeyboardInterrupt:
        log_combined("Execução interrompida pelo usuário", "warning")
        if GUI_AVAILABLE and gui:
            update_gui_status(status="Interrompido pelo usuário")
            
    except Exception as e:
        log_combined(f"Erro fatal: {e}", "error")
        if GUI_AVAILABLE and gui:
            update_gui_status(status=f"Erro fatal: {str(e)}")
            
    finally:
        # SEMPRE manter a GUI aberta para decisão do usuário
        if GUI_AVAILABLE and gui is not None:
            log_combined("", "info")
            log_combined("🎯 O que você deseja fazer?", "header")
            log_combined("1. Pressione ESC para sair", "info")
            log_combined("2. Conecte outro celular e reinicie", "info")
            log_combined("", "info")

            try:
                waiting = True
                clock = pygame.time.Clock()

                # Loop de espera seguro
                while waiting and getattr(gui, 'running', False):
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                            waiting = False
                            gui.running = False
                            log_combined("Aplicação encerrada", "success")

                    # Atualizar GUI se tiver método draw_interface
                    if hasattr(gui, 'draw_interface'):
                        gui.draw_interface()

                    clock.tick(30)

            except Exception as e:
                log_combined(f"Erro: {e}", "error")
                time_module.sleep(3)

            # Garantir encerramento da GUI
            gui.running = False
            if gui_thread and gui_thread.is_alive():
                gui_thread.join(timeout=2.0)

if __name__ == "__main__":
    main()