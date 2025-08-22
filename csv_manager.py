import csv
import os
from datetime import datetime

class CSVManager:
    def __init__(self, args):
        if len(args) > 1:
            self.csv_path = args[1]
        else:
            self.csv_path = input("Digite o caminho do CSV: ").strip()
        
        # Garantir que o diretório existe
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
    
    def criar_csv_inicial(self):
        """Cria CSV inicial se não existir"""
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['numero', 'status', 'data_processamento', 'tentativas']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
            print(f"CSV criado em: {self.csv_path}")
    
    def ler_contatos(self):
        """Lê contatos do CSV"""
        contatos = []
        try:
            with open(self.csv_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row.get('status') not in ['SUCESSO', 'PROCESSADO']:
                        contatos.append({
                            'numero': row['numero'],
                            'status': row.get('status', 'PENDENTE')
                        })
            return contatos
        except FileNotFoundError:
            print(f"Arquivo {self.csv_path} não encontrado")
            return []
        except Exception as e:
            print(f"Erro ao ler CSV: {e}")
            return []
    
    def marcar_como_processado(self, numero, status):
        """Marca um número como processado"""
        try:
            # Ler todas as linhas
            rows = []
            with open(self.csv_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                fieldnames = reader.fieldnames
                for row in reader:
                    if row['numero'] == numero:
                        row['status'] = status
                        row['data_processamento'] = datetime.now().isoformat()
                        row['tentativas'] = str(int(row.get('tentativas', 0)) + 1)
                    rows.append(row)
            
            # Reescrever o arquivo
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
                
        except Exception as e:
            print(f"Erro ao atualizar CSV: {e}")