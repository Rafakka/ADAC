import csv
from logger import log_combined
from gui_manager import update_gui_status_safe, is_gui_paused, should_stop

def load_contacts(file_path):
    """
    Carrega contatos de um CSV.
    Retorna lista de dicionários: [{'nome': ..., 'telefone': ...}, ...]
    """
    contatos = []
    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                contatos.append(row)
        log_combined(f"✅ {len(contatos)} contatos carregados do arquivo {file_path}", "success")
        return contatos
    except FileNotFoundError:
        log_combined(f"❌ Arquivo não encontrado: {file_path}", "error")
        return []
    except Exception as e:
        log_combined(f"❌ Erro ao ler CSV: {e}", "error")
        return []

def process_contacts(contatos, gui=None, celular_id=None):
    """
    Processa lista de contatos.
    Pode atualizar GUI, log e estatísticas.
    Retorna tupla: (sucesso, falha)
    """
    total = len(contatos)
    sucesso = 0
    falha = 0

    for i, contato in enumerate(contatos, start=1):
        # Checa se deve parar (GUI fechada ou ESC)
        if should_stop():
            log_combined("Processamento interrompido pelo usuário", "warning", gui)
            break

        # Pausa se GUI estiver pausada
        while is_gui_paused():
            if gui and hasattr(gui, 'draw_interface'):
                gui.draw_interface()

        try:
            nome = contato.get('nome', 'Desconhecido')
            telefone = contato.get('telefone', 'N/A')
            
            # Aqui iria a lógica de discagem, API ou ADB
            # Por agora, apenas simulamos processamento
            log_combined(f"📞 Discando para {nome} ({telefone})...", "info", gui)
            
            # Simulação de sucesso
            sucesso += 1

        except Exception as e:
            log_combined(f"❌ Falha ao processar {contato}: {e}", "error", gui)
            falha += 1

        # Atualiza GUI e status
        if gui:
            update_gui_status_safe(
                total=total,
                processados=i,
                sucesso=sucesso,
                falha=falha,
                current=nome
            )
            gui.draw_interface()

    log_combined(f"✅ Processamento concluído: {sucesso} sucesso(s), {falha} falha(s)", "success", gui)
    return sucesso, falha
