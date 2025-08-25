#!/usr/bin/env python3
"""
Gerenciador de configurações do ADAC
"""

import os
from config import CONFIG_FILE

def mostrar_configuracoes():
    """Mostra as configurações atuais"""
    print("🔧 Configurações atuais do ADAC:")
    print("=" * 40)
    
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    print(f"   {line}")
    else:
        print("   ⚠️  Arquivo de configuração não encontrado")
        print("   💡 Use: python config_manager.py --edit para criar")

def editar_configuracoes():
    """Edita as configurações"""
    print("✏️  Editando configurações do ADAC")
    print("=" * 40)
    
    # Configurações atuais
    config_lines = []
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config_lines = f.readlines()
    
    # Se não existir, criar com padrões
    if not config_lines:
        config_lines = [
            "# Configurações do ADAC - Auto Discador\n",
            "# Formato: chave=valor\n\n",
            "# Número para onde as ligações serão transferidas\n",
            "numero_redirecionamento=11999999999\n\n",
            "# Tempo em segundos para aguardar discagem\n",
            "tempo_discagem=8\n\n",
            "# Tempo em segundos para aguardar transferência\n",
            "tempo_transferencia=12\n"
        ]
    
    # Mostrar e editar
    novas_linhas = []
    for line in config_lines:
        line = line.rstrip()
        if line and '=' in line and not line.startswith('#'):
            key, value = line.split('=', 1)
            print(f"🔹 {key} = {value}")
            novo_valor = input(f"   Novo valor para '{key}' (Enter para manter): ").strip()
            if novo_valor:
                line = f"{key}={novo_valor}"
        novas_linhas.append(line + '\n')
    
    # Salvar
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        f.writelines(novas_linhas)
    
    print("✅ Configurações salvas!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--edit":
        editar_configuracoes()
    else:
        mostrar_configuracoes()
        print("\n💡 Use: python config_manager.py --edit para editar configurações")