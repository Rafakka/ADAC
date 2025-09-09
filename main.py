import sys
import threading
import time as time_module
import logging
import os

os.environ['SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR'] = '0'
os.environ['SDL_VIDEO_X11_SHM'] = '0'

from csv_manager import CSVManager
from caller import discar_e_transferir
from config import CONTATOS_DIR, LOGS_DIR, GUI_ENABLED
from logger_manager import log_combined, init_gui_logger, setup_logging
from hardware_manager import verificar_adb, detectar_dispositivos

logger = setup_logging()

GUI_AVAILABLE = False
if GUI_ENABLED:
    try:
        from gui_integrada import init_gui, update_gui_status, is_gui_paused, should_stop
        GUI_AVAILABLE = True
    except ImportError as e:
        log_combined(f"GUI não disponível: {e}", "error")
        GUI_AVAILABLE = False

# Inicializar logger com status da GUI
init_gui_logger(GUI_AVAILABLE)

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
            # Atualizar logger com novo status
            init_gui_logger(False)

    try:
        log_combined("=== ADAC - Auto Discador iniciado ===")
        log_combined(f"📁 Pasta de contatos: {CONTATOS_DIR}")
        log_combined(f"📁 Pasta de logs: {LOGS_DIR}")
        
        if GUI_AVAILABLE and gui:
            update_gui_status(status="Inicializando...")

        if not verificar_adb():
            log_combined("ADB não disponível.", "error")
            if GUI_AVAILABLE:
                update_gui_status(status="Erro - ADB não disponível")
            sys.exit(1)
        
        CELULAR = None
        tentando_conectar = True

        while tentando_conectar:
            if GUI_AVAILABLE:
                while is_gui_paused() and not should_stop():
                    time_module.sleep(0.5)
                    
            devices = detectar_dispositivos()

            if devices:
                CELULAR = devices[0]
                log_combined(f"Usando celular:{CELULAR}","sucess")
                if GUI_AVAILABLE:
                    update_gui_status(device=f"Conectado:{CELULAR}")
                tentando_conectar = False
            else:
                log_combined("Nenhum celular detectado, aguardado conecção...","warning")
                if GUI_AVAILABLE:
                    update_gui_status(status="Aguardando dispositivo...")
                
                for _ in range(3):
                    time_module.sleep(1)
                if GUI_AVAILABLE and should_stop():
                    log_combined("Execução interrompida pelo usuario","warning")
                    sys.exit(0)

        # CSVManager com novo comportamento
        csv_manager = CSVManager()
        csv_path = csv_manager.get_csv_path()

        # Verificar se o arquivo existe
        if not csv_manager.arquivo_existente():
            log_combined("❌ Nenhum arquivo CSV encontrado!", "error")
            log_combined("", "warning")
            log_combined("📋 SOLUÇÃO:", "header")
            log_combined("1. Crie um arquivo CSV com os contatos", "warning")
            log_combined("2. Coloque na pasta: contatos/", "warning")
            log_combined("3. Formato: numero,nome,data_nascimento,status,...", "warning")
            log_combined("4. Exemplo: 11999999999,João Silva,15/05/1990,PENDENTE", "warning")
            log_combined("", "warning")
            log_combined("💡 Pressione ESC para fechar e corrigir", "header")
            
            if GUI_AVAILABLE:
                update_gui_status(
                    status="Erro - CSV não encontrado",
                    csv="Arquivo não encontrado",
                    current="Aguardando correção"
                )
        else:
            log_combined(f"📋 Arquivo CSV encontrado: {csv_path}", "success")
            
            if GUI_AVAILABLE:
                update_gui_status(csv=f"Carregado: {os.path.basename(csv_path)}")

        # Ler contatos (tenta mesmo se arquivo não existir - retorna lista vazia)
        contatos = csv_manager.ler_contatos()
        total_contatos = len(contatos)

        # Atualizar a barra de progresso independentemente
        if GUI_AVAILABLE:
            update_gui_status(
                total=total_contatos,
                processados=0,
                sucesso=0,
                falha=0,
                status="Aguardando" if total_contatos == 0 else "Pronto para discagem"
            )

        if total_contatos == 0:
            log_combined("ℹ️  Nenhum contato para processar.", "warning")
            if not csv_manager.arquivo_existente():
                log_combined("💡 Crie um arquivo CSV na pasta contatos/", "warning")
            else:
                log_combined("💡 Adicione números no arquivo CSV existente", "warning")
        else:
            log_combined(f"✅ Encontrados {total_contatos} contatos para discar", "success")

        sucesso_count = 0
        falha_count = 0
        
        for i, contato in enumerate(contatos, 1):
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

        log_combined(f"=== ADAC - Processamento concluído ===", "success")
        log_combined(f"📊 Total: {total_contatos} contatos", "success")
        log_combined(f"✅ Sucesso: {sucesso_count}", "success")
        log_combined(f"❌ Falha: {falha_count}", "warning" if falha_count > 0 else "success")
        log_combined(f"📄 Log salvo em: {log_file}")
        
        if GUI_AVAILABLE:
            update_gui_status(
                status="Concluído - Pressione ESC",
                processados=total_contatos,
                sucesso=sucesso_count,
                falha=falha_count,
                current="Aguardando para fechar"
            )
            
            log_combined("Processamento concluído. Pressione ESC para fechar.", "success")

    except KeyboardInterrupt:
        log_combined("Execução interrompida pelo usuário", "warning")
        if GUI_AVAILABLE and gui:
            update_gui_status(status="Interrompido pelo usuário")
            
    except Exception as e:
        log_combined(f"Erro fatal: {e}", "error")
        if GUI_AVAILABLE and gui:
            update_gui_status(status=f"Erro fatal: {str(e)}")   
    finally:
        if GUI_AVAILABLE and gui:
            try:
                # Usar fechamento seguro
                if hasattr(gui, 'safe_quit'):
                    gui.safe_quit()
                else:
                    gui.running = False
                
                # Esperar um pouco
                time_module.sleep(0.5)
                
                # Fazer join com timeout
                if gui_thread and gui_thread.is_alive():
                    gui_thread.join(timeout=1.0)
                    
            except Exception as e:
                log_combined(f"Erro no fechamento: {e}", "error")
                
            
if __name__ == "__main__":
    main()