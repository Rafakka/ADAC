#!/usr/bin/env python3
"""
Teste rápido da interface gráfica
"""

import pygame
import sys
import os
from datetime import datetime

# Configuração básica do PyGame
pygame.init()

# Configurações da janela
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ADAC - Teste de Interface")

# Cores
CORES = {
    'fundo': (0, 12, 24),      # Azul escuro
    'texto': (0, 255, 0),      # Verde
    'erro': (255, 50, 50),     # Vermelho
    'sucesso': (50, 255, 50),  # Verde
    'alerta': (255, 255, 0),   # Amarelo
    'destaque': (0, 150, 255)  # Azul
}

# Fontes
fonte = pygame.font.SysFont("Consolas", 16)
fonte_titulo = pygame.font.SysFont("Consolas", 24, bold=True)

# Mensagens de exemplo
mensagens = [
    ("✅ Sistema inicializado com sucesso", CORES['sucesso']),
    ("📱 Dispositivo detectado: 0082825555", CORES['texto']),
    ("📋 CSV carregado: 3 contatos encontrados", CORES['texto']),
    ("⚠️  Tempo de discagem configurado: 8 segundos", CORES['alerta']),
    ("🔧 Iniciando processo de discagem...", CORES['destaque']),
    ("📞 Discando para: João Silva (11 99999-9999)", CORES['texto']),
    ("✅ Chamada atendida! Transferindo...", CORES['sucesso']),
    ("✅ Transferência concluída com sucesso", CORES['sucesso']),
    ("📞 Discando para: Maria Santos (11 88888-8888)", CORES['texto']),
    ("❌ Chamada não atendida", CORES['erro']),
    ("📞 Discando para: Carlos Oliveira (11 77777-7777)", CORES['texto']),
    ("✅ Chamada atendida! Transferindo...", CORES['sucesso']),
    ("✅ Transferência concluída com sucesso", CORES['sucesso']),
    ("🎯 Processamento concluído: 2/3 contatos atendidos", CORES['sucesso']),
]

def desenhar_interface():
    """Desenha a interface completa"""
    # Fundo
    screen.fill(CORES['fundo'])
    
    # Título
    titulo = fonte_titulo.render("ADAC - AUTO DISCADOR (MODO TESTE)", True, CORES['destaque'])
    screen.blit(titulo, (20, 20))
    
    # Linha separadora
    pygame.draw.line(screen, CORES['destaque'], (20, 60), (WIDTH - 20, 60), 2)
    
    # Status
    status = fonte.render("Status: Testando interface gráfica | Pressione ESPAÇO para adicionar mensagem | ESC para sair", 
                         True, CORES['texto'])
    screen.blit(status, (20, HEIGHT - 30))
    
    # Área de logs
    pygame.draw.rect(screen, (20, 30, 50), (20, 80, WIDTH - 40, HEIGHT - 120), 0, 5)
    pygame.draw.rect(screen, CORES['destaque'], (20, 80, WIDTH - 40, HEIGHT - 120), 2, 5)
    
    # Mensagens
    y = 100
    for texto, cor in mensagens[-15:]:  # Mostrar apenas as últimas 15 mensagens
        texto_surface = fonte.render(texto, True, cor)
        screen.blit(texto_surface, (40, y))
        y += 25
    
    pygame.display.flip()

def main():
    clock = pygame.time.Clock()
    running = True
    
    print("🎮 Teste da Interface Gráfica")
    print("📋 Pressione ESPAÇO para adicionar mensagens")
    print("🚪 Pressione ESC para sair")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                elif event.key == pygame.K_SPACE:
                    # Adicionar nova mensagem de teste
                    from datetime import datetime
                    hora = datetime.now().strftime("%H:%M:%S")
                    nova_msg = f"[{hora}] Mensagem de teste #{len(mensagens) + 1}"
                    mensagens.append((nova_msg, CORES['texto']))
                    print(f"📝 Mensagem adicionada: {nova_msg}")
                
                elif event.key == pygame.K_s:
                    # Mensagem de sucesso
                    mensagens.append(("✅ Ação concluída com sucesso!", CORES['sucesso']))
                
                elif event.key == pygame.K_e:
                    # Mensagem de erro
                    mensagens.append(("❌ Erro ao processar solicitação", CORES['erro']))
        
        desenhar_interface()
        clock.tick(60)
    
    pygame.quit()
    print("👋 Teste finalizado!")
    return True

if __name__ == "__main__":
    main()