import csv
from datetime import datetime
import logging
import os
from caller import discar_e_transferir
from logger import log_combined
from csv_manager import CSVManager 

def load_contacts(csv_path="contatos.csv", gui=None):
    """Carrega contatos do CSV"""
    contatos = []
    if not os.path.exists(csv_path):
        logging.error(f"Arquivo de contatos não encontrado: {csv_path}")
        return contatos
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            contatos.append(row)
    return contatos

def process_contacts(contatos, celular=None, gui=None, csv_manager=None):
    """Processa contatos (discagem real)"""
    sucesso, falha = 0, 0

    for i, contato in enumerate(contatos, 1):
        nome = contato.get("nome")
        numero = contato.get("telefone")
        nascimento = contato.get("data_nascimento", "")

        log_combined(f"📞 Processando {i}/{len(contatos)}: {nome} ({numero})", "info", gui)

        status = discar_e_transferir(numero, nome, nascimento, celular, csv_manager)

        if status == "ATENDEU":
            sucesso += 1
            log_combined(f"✅ {nome} ATENDEU e foi transferido", "success", gui)
        elif status in ["NAO_ATENDEU", "FALHA_DISCAGEM", "INDEFINIDO", "ERRO"]:
            falha += 1
            log_combined(f"❌ {nome} - {status}", "error", gui)
        else:
            falha += 1
            log_combined(f"⚠️ {nome} - status inesperado: {status}", "warning", gui)

        if gui:
            gui.update_status(
                processados=i,
                sucesso=sucesso,
                falha=falha,
                current=f"{nome} ({numero})"
            )

    return sucesso, falha


def salvar_log_csv(contatos, sucesso_dict, falha_dict):
    os.makedirs("logs", exist_ok=True)
    filepath = os.path.join("logs", f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Contato", "Status"])
        for contato in contatos:
            status = "✅" if contato in sucesso_dict else "❌"
            writer.writerow([contato, status])
    
    log_combined(f"📂 Log salvo em {filepath}", "success")
