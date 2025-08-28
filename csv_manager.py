import os
from models import CSVManager
from logger import log_combined, update_gui_status_safe
from config import CONTATOS_DIR, CSV_DEFAULT_PATH
import time as time_module

def encontrar_arquivo_csv():
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

def load_contacts(gui):
    csv_path = encontrar_arquivo_csv()
    log_combined(f"📋 Usando arquivo CSV: {csv_path}")
    update_gui_status_safe(gui, csv=f"Carregado: {os.path.basename(csv_path)}")
    
    csv_manager = CSVManager([csv_path])
    csv_manager.criar_csv_inicial()
    
    contatos = csv_manager.ler_contatos()
    log_combined(f"Encontrados {len(contatos)} contatos para discar", "success")
    update_gui_status_safe(gui, total=len(contatos), status="Pronto para discagem")
    
    return csv_manager, contatos

def process_contacts(contatos, csv_manager, celular, gui):
    from caller import discar_e_transferir  # import local evita circular import
    from gui_manager import is_gui_paused, should_stop
    sucesso_count, falha_count = 0, 0

    for i, contato in enumerate(contatos, 1):
        if gui:
            while is_gui_paused() and not should_stop():
                time_module.sleep(0.5)
            if should_stop():
                log_combined("Execução interrompida pelo usuário", "warning")
                break

        numero = contato["numero"]
        nome = contato.get("nome", "Não informado")
        data_nascimento = contato.get("data_nascimento", "Não informada")

        log_combined(f"[{i}/{len(contatos)}] Processando: {nome}")
        update_gui_status_safe(gui, processados=i-1, sucesso=sucesso_count, falha=falha_count,
                               current=f"{nome} - {numero}", status="Discando...")

        try:
            resultado = discar_e_transferir(numero, nome, data_nascimento, celular, csv_manager)
            if resultado == "ATENDEU":
                sucesso_count += 1
                log_combined(f"✅ {nome} ({data_nascimento}) - {numero} - ATENDEU", "success")
            else:
                falha_count += 1
                log_combined(f"❌ {nome} ({data_nascimento}) - {numero} - NÃO ATENDEU", "warning")

            update_gui_status_safe(gui, processados=i, sucesso=sucesso_count, falha=falha_count)
            time_module.sleep(3)

        except Exception as e:
            falha_count += 1
            log_combined(f"Erro ao processar {numero}: {e}", "error")
            csv_manager.marcar_como_processado(numero, "ERRO", nome, data_nascimento)
            update_gui_status_safe(gui, processados=i, falha=falha_count)

    return sucesso_count, falha_count