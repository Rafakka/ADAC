import csv
from logger import log_combined

def load_contacts(csv_path="contatos.csv", gui=None):
    """Carrega contatos do CSV"""
    contatos = []
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                contatos.append(row)
        log_combined(f"{len(contatos)} contatos carregados do CSV", "success", gui)
    except Exception as e:
        log_combined(f"Erro ao carregar CSV: {e}", "error", gui)
    return contatos

def process_contacts(contatos, celular=None, gui=None):
    """Processa contatos (simula discagem)"""
    sucesso, falha = 0, 0
    for i, contato in enumerate(contatos,1):
        log_combined(f"Processando contato {i}/{len(contatos)}: {contato.get('nome')}", "info", gui)
        # Simulação: alterna sucesso/falha
        if i%2==0:
            sucesso+=1
            log_combined(f"Contato {contato.get('nome')} discado com sucesso", "success", gui)
        else:
            falha+=1
            log_combined(f"Falha ao discar contato {contato.get('nome')}", "error", gui)
        if gui:
            gui.update_status(processados=i, sucesso=sucesso, falha=falha, current=contato.get("nome"))
    return sucesso, falha
