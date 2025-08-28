import csv
import os
from datetime import datetime
from caller import discar_e_transferir
from config import CONTATOS_DIR, CSV_DEFAULT_PATH
from gui_integrada import is_gui_paused, should_stop
from gui_manager import update_gui_status_safe
from logger import log_combined
from main import GUI_AVAILABLE
import time as time_module 

def load_contacts(gui):
    csv_path = encontrar_arquivo_csv()
    log_combined(f"📋 Usando arquivo CSV: {csv_path}")
    update_gui_status_safe(gui, csv=f"Carregado: {os.path.basename(csv_path)}")
    
    csv_manager = CSVManager([csv_path])
    csv_manager.criar_csv_inicial()
    
    contatos = csv_manager.ler_contatos()
    total = len(contatos)
    log_combined(f"Encontrados {total} contatos para discar", "success")
    update_gui_status_safe(gui, total=total, status="Pronto para discagem")
    
    return csv_manager, contatos

def process_contacts(contatos, csv_manager, celular, gui):
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
            continue

    return sucesso_count, falha_count


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
    

class CSVManager:
    def __init__(self, args=None):
        self.csv_path = CSV_DEFAULT_PATH
        if args and len(args) > 1:
            self.csv_path = args[1]
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
    
    def criar_csv_inicial(self):
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['numero', 'nome', 'data_nascimento', 'status', 'data_processamento', 'tentativas']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
    
    def ler_contatos(self):
        contatos = []
        try:
            with open(self.csv_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row.get('status') not in ['SUCESSO', 'PROCESSADO']:
                        contatos.append({
                            'numero': row['numero'],
                            'nome': row.get('nome', ''),
                            'data_nascimento': row.get('data_nascimento', ''),
                            'status': row.get('status', 'PENDENTE')
                        })
            return contatos
        except:
            return []
    
    def marcar_como_processado(self, numero, status, nome="", data_nascimento=""):
        try:
            rows = []
            with open(self.csv_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                fieldnames = reader.fieldnames
                
                for row in reader:
                    if row['numero'] == numero:
                        # Atualizar campos
                        row['status'] = status
                        row['data_processamento'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        
                        # Corrigir tentativas - método mais seguro
                        tentativas = row.get('tentativas', '').strip()
                        if not tentativas or not tentativas.isdigit():
                            row['tentativas'] = '1'
                        else:
                            row['tentativas'] = str(int(tentativas) + 1)
                        
                        # Atualizar nome e data se fornecidos
                        if nome:
                            row['nome'] = nome
                        if data_nascimento:
                            row['data_nascimento'] = data_nascimento
                    
                    rows.append(row)
            
            # Escrever de volta
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
                
        except Exception as e:
            print(f"Erro ao atualizar CSV: {e}")