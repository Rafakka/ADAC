import subprocess
import sys
import threading
import time as time_module  # Renomear para evitar conflito
import logging
import os
import pygame

os.environ['SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR'] = '0'
os.environ['SDL_VIDEO_X11_SHM'] = '0'  # Desativa shared memory

from csv_manager import CSVManager, encontrar_arquivo_csv
from caller import discar_e_transferir
from config import ADB_PATH, CONTATOS_DIR, LOGS_DIR, CSV_DEFAULT_PATH, GUI_ENABLED
from logger import log_combined, mostrar_ajuda_erro
from adb_manager import verificar_adb
from hardware_manager import detectar_dispositivos, esperar_celular_conectar

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