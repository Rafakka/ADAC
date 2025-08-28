import csv
import os
from datetime import datetime
from config import CONTATOS_DIR, CSV_DEFAULT_PATH

class CSVManager:
    def __init__(self, csv_path=None):
        # Se não foi passado um caminho, encontrar automaticamente
        if csv_path is None:
            self.csv_path = self.encontrar_arquivo_csv()
        else:
            self.csv_path = csv_path
        
        # Verificar se o arquivo existe
        self.arquivo_existe = os.path.exists(self.csv_path)
    
    def encontrar_arquivo_csv(self):
        """Encontra automaticamente o arquivo CSV na pasta contatos/"""
        try:
            # Verificar se existe o arquivo padrão
            if os.path.exists(CSV_DEFAULT_PATH):
                return CSV_DEFAULT_PATH
            
            # Procurar por qualquer arquivo CSV na pasta contatos/
            if os.path.exists(CONTATOS_DIR):
                for arquivo in os.listdir(CONTATOS_DIR):
                    if arquivo.lower().endswith('.csv'):
                        caminho_completo = os.path.join(CONTATOS_DIR, arquivo)
                        if os.path.exists(caminho_completo):
                            return caminho_completo
            
            # Se não encontrou nenhum arquivo CSV
            return CSV_DEFAULT_PATH  # Retorna o caminho padrão, mas o arquivo não existe
            
        except Exception as e:
            print(f"Erro ao procurar arquivo CSV: {e}")
            return CSV_DEFAULT_PATH
    
    def arquivo_existente(self):
        """Retorna True se o arquivo CSV existe"""
        return self.arquivo_existe
    
    def criar_csv_inicial(self):
        """NÃO cria CSV automaticamente - apenas verifica"""
        if not self.arquivo_existe:
            return False  # Indica que não criou arquivo
        return True  # Arquivo já existe
    
    def ler_contatos(self):
        """Lê contatos do CSV se o arquivo existir"""
        if not self.arquivo_existe:
            return []  # Retorna lista vazia se arquivo não existe
        
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
        except FileNotFoundError:
            print(f"Arquivo {self.csv_path} não encontrado")
            return []
        except Exception as e:
            print(f"Erro ao ler CSV: {e}")
            return []
    
    def marcar_como_processado(self, numero, status, nome="", data_nascimento=""):
        """Marca um número como processado (apenas se arquivo existir)"""
        if not self.arquivo_existe:
            return False  # Não faz nada se arquivo não existe
            
        try:
            # Ler todas as linhas
            rows = []
            with open(self.csv_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                fieldnames = reader.fieldnames
                for row in reader:
                    if row['numero'] == numero:
                        row['status'] = status
                        row['data_processamento'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        
                        # Corrigir tentativas
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
            
            # Reescrever o arquivo
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
                
            return True
        except Exception as e:
            print(f"Erro ao atualizar CSV: {e}")
            return False
    
    def get_csv_path(self):
        """Retorna o caminho do CSV em uso"""
        return self.csv_path
    
    def listar_arquivos_csv(self):
        """Lista todos os arquivos CSV disponíveis na pasta contatos/"""
        try:
            if not os.path.exists(CONTATOS_DIR):
                return []
            
            arquivos_csv = []
            for arquivo in os.listdir(CONTATOS_DIR):
                if arquivo.lower().endswith('.csv'):
                    arquivos_csv.append(arquivo)
            
            return arquivos_csv
        except Exception as e:
            print(f"Erro ao listar arquivos CSV: {e}")
            return []