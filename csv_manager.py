import csv
import os
import logging
from datetime import datetime

class CSVManager:
    def __init__(self, args):
        if len(args) > 1:
            self.csv_path = args[1]
        else:
            self.csv_path = input("Digite o caminho do CSV: ").strip()
        
        # Garantir que o diretório existe
        if self.csv_path:  # Evitar erro se caminho for vazio
            os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
        
        logging.info(f"📁 Gerenciador CSV inicializado: {self.csv_path}")
    
    def criar_csv_inicial(self):
        """Cria CSV inicial se não existir"""
        if not os.path.exists(self.csv_path):
            try:
                with open(self.csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['numero', 'status', 'data_processamento', 'tentativas']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                logging.info(f"✅ CSV criado em: {self.csv_path}")
                return True
            except Exception as e:
                logging.error(f"❌ Erro ao criar CSV: {e}")
                return False
        else:
            logging.info(f"📄 CSV já existe: {self.csv_path}")
            return True
    
    def ler_contatos(self):
        """Lê contatos do CSV"""
        contatos = []
        try:
            if not os.path.exists(self.csv_path):
                logging.warning(f"⚠️ Arquivo {self.csv_path} não encontrado")
                return contatos
            
            with open(self.csv_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Ignorar linhas vazias ou sem número
                    if not row.get('numero') or not row['numero'].strip():
                        continue
                    
                    # Processar apenas pendentes ou com status não finalizado
                    status_atual = row.get('status', 'PENDENTE').strip().upper()
                    if status_atual not in ['SUCESSO', 'PROCESSADO', 'FALHA', 'ERRO']:
                        contatos.append({
                            'numero': row['numero'].strip(),
                            'status': status_atual,
                            'tentativas': int(row.get('tentativas', 0))
                        })
            
            logging.info(f"📋 {len(contatos)} contatos para processar")
            return contatos
            
        except FileNotFoundError:
            logging.error(f"❌ Arquivo {self.csv_path} não encontrado")
            return []
        except Exception as e:
            logging.error(f"💥 Erro ao ler CSV: {e}")
            return []
    
    def marcar_como_processado(self, numero, status):
        """Marca um número como processado"""
        try:
            if not os.path.exists(self.csv_path):
                logging.error(f"❌ Arquivo CSV não existe: {self.csv_path}")
                return False
            
            # Ler todas as linhas
            rows = []
            fieldnames = ['numero', 'status', 'data_processamento', 'tentativas']
            
            with open(self.csv_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                fieldnames = reader.fieldnames or ['numero', 'status', 'data_processamento', 'tentativas']
                
                for row in reader:
                    if row.get('numero', '').strip() == numero.strip():
                        row['status'] = status
                        row['data_processamento'] = datetime.now().isoformat()
                        row['tentativas'] = str(int(row.get('tentativas', 0)) + 1)
                        logging.info(f"✅ Marcado {numero} como {status}")
                    rows.append(row)
            
            # Reescrever o arquivo
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            
            return True
                
        except Exception as e:
            logging.error(f"💥 Erro ao atualizar CSV: {e}")
            return False
    
    def adicionar_contato(self, numero, status="PENDENTE"):
        """Adiciona um novo contato ao CSV"""
        try:
            # Verificar se o número já existe
            contatos_existentes = self.ler_contatos()
            for contato in contatos_existentes:
                if contato['numero'] == numero:
                    logging.warning(f"⚠️ Número {numero} já existe no CSV")
                    return False
            
            # Adicionar novo contato
            with open(self.csv_path, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['numero', 'status', 'data_processamento', 'tentativas']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writerow({
                    'numero': numero,
                    'status': status,
                    'data_processamento': '',
                    'tentativas': '0'
                })
            
            logging.info(f"✅ Número {numero} adicionado ao CSV")
            return True
            
        except Exception as e:
            logging.error(f"💥 Erro ao adicionar contato: {e}")
            return False
    
    def limpar_csv(self):
        """Limpa o CSV, mantendo apenas o cabeçalho"""
        try:
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['numero', 'status', 'data_processamento', 'tentativas']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
            
            logging.info("✅ CSV limpo com sucesso")
            return True
            
        except Exception as e:
            logging.error(f"💥 Erro ao limpar CSV: {e}")
            return False
    
    def exportar_resultados(self, output_path):
        """Exporta apenas os resultados processados"""
        try:
            contatos = self.ler_contatos()
            processados = [c for c in contatos if c['status'] in ['SUCESSO', 'FALHA', 'ERRO']]
            
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['numero', 'status', 'data_processamento', 'tentativas']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for contato in processados:
                    writer.writerow(contato)
            
            logging.info(f"✅ Resultados exportados para: {output_path}")
            return True
            
        except Exception as e:
            logging.error(f"💥 Erro ao exportar resultados: {e}")
            return False