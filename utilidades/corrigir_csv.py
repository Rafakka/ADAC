#!/usr/bin/env python3
"""
Script para corrigir o arquivo CSV existente
"""

import csv
from config import CSV_DEFAULT_PATH

def corrigir_csv():
    print("🔧 Corrigindo arquivo CSV...")
    
    try:
        # Ler arquivo
        rows = []
        with open(CSV_DEFAULT_PATH, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            fieldnames = reader.fieldnames
            
            for row in reader:
                # Corrigir campo tentativas vazio
                if row.get('tentativas', '').strip() == '':
                    row['tentativas'] = '0'
                rows.append(row)
        
        # Escrever corrigido
        with open(CSV_DEFAULT_PATH, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print("✅ CSV corrigido com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao corrigir CSV: {e}")

if __name__ == "__main__":
    corrigir_csv()