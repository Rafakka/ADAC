import csv
import os
from datetime import datetime
from config import CONTATOS_DIR, CSV_DEFAULT_PATH
from logger import log_combined

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