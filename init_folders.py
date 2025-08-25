#!/usr/bin/env python3
"""
Script para criar a estrutura de pastas automaticamente
"""

import os
from config import CONTATOS_DIR, LOGS_DIR

def criar_estrutura_pastas():
    """Cria a estrutura de pastas necessária"""
    print("📁 Criando estrutura de pastas...")
    
    # Criar pastas principais
    os.makedirs(CONTATOS_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    print(f"✅ Pasta de contatos: {CONTATOS_DIR}")
    print(f"✅ Pasta de logs: {LOGS_DIR}")
    
    # Verificar se existe arquivo CSV
    csv_path = os.path.join(CONTATOS_DIR, "contatos.csv")
    if not os.path.exists(csv_path):
        print("📋 Criando arquivo CSV modelo...")
        with open(csv_path, 'w', encoding='utf-8') as f:
            f.write("numero,nome,data_nascimento,status,data_processamento,tentativas\n")
            f.write("0082825555,João Silva,15/05/1990,PENDENTE,,\n")
            f.write("11999999999,Maria Santos,20/08/1985,PENDENTE,,\n")
        print(f"✅ Arquivo CSV criado: {csv_path}")
    
    print("🎯 Estrutura de pastas criada com sucesso!")
    print("💡 Adicione seus contatos no arquivo contatos/contatos.csv")

if __name__ == "__main__":
    criar_estrutura_pastas()