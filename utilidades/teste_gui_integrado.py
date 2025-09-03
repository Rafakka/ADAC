#!/usr/bin/env python3
"""
Teste da GUI integrada com o ADAC
"""

import pygame
from datetime import datetime
import time
import random

class ADACTestGUI:
    def __init__(self):
        pygame.init()
        self.width = 900
        self.height = 700
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("ADAC - Teste de Interface")
        
        # Cores
        self.colors = {
            'bg': (0, 12, 24),
            'text': (0, 255, 0),
            'error': (255, 50, 50),
            'success': (50, 255, 50),
            'warning': (255, 255, 0),
            'header': (0, 150, 255),
            'border': (0, 80, 160)
        }
        
        # Fontes
        self.font = pygame.font.SysFont("Consolas", 16)
        self.title_font = pygame.font.SysFont("Consolas", 24, bold=True)
        
        # Dados de teste
        self.lines = []
        self.status = "Testando"
        self.device_status = "Dispositivo simulado: 0082825555"
        self.csv_status = "CSV teste: 5 contatos"
        self.contador = 0
        
        self.init_display()
    
    def init_display(self):
        """Inicializa o display com mensagens de teste"""
        self.add_line("═" * 80, self.colors['border'])
        self.add_line("    ADAC - MODO DE TESTE DA INTERFACE", self.colors['header'])
        self.add_line("═" * 80, self.colors['border'])
        self.add_line(" Este é um teste da interface gráfica")
        self.add_line(" Pressione F1 para simular discagem")
        self.add_line(" Pressione F2 para simular erro")
        self.add_line(" Pressione F3 para adicionar mensagem")
        self.add_line(" Pressione ESC para sair")
        self.add_line("═" * 80, self.colors['border'])
    
    def add_line(self, text, color=None):
        """Adiciona uma linha ao buffer"""
        if color is None:
            color = self.colors['text']
        self.lines.append((text, color))
        if len(self.lines) > 20:
            self.lines = self.lines[-20:]
    
    def simular_discagem(self):
        """Simula o processo de discagem"""
        self.contador += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.add_line(f"[{timestamp}] 📞 Iniciando discagem #{self.contador}", self.colors['text'])
        time.sleep(0.5)
        
        # Simular aleatoriamente sucesso ou falha
        if random.random() > 0.3:  # 70% de chance de sucesso
            self.add_line(f"[{timestamp}] ✅ Chamada atendida!", self.colors['success'])
            time.sleep(0.3)
            self.add_line(f"[{timestamp}] 🔄 Transferindo chamada...", self.colors['warning'])
            time.sleep(0.5)
            self.add_line(f"[{timestamp}] ✅ Transferência concluída", self.colors['success'])
        else:
            self.add_line(f"[{timestamp}] ❌ Chamada não atendida", self.colors['error'])
    
    def draw_interface(self):
        """Desenha a interface completa"""
        self.screen.fill(self.colors['bg'])
        
        # Título
        title = self.title_font.render("ADAC - TESTE DE INTERFACE GRÁFICA", True, self.colors['header'])
        self.screen.blit(title, (20, 15))
        
        # Painel de status
        pygame.draw.rect(self.screen, (30, 30, 50), (20, 60, self.width - 40, 80), 0, 5)
        pygame.draw.rect(self.screen, self.colors['border'], (20, 60, self.width - 40, 80), 2, 5)
        
        status_texts = [
            f"Status: {self.status}",
            f"Dispositivo: {self.device_status}",
            f"CSV: {self.csv_status}",
            f"Discagens simuladas: {self.contador}"
        ]
        
        for i, text in enumerate(status_texts):
            text_surf = self.font.render(text, True, self.colors['text'])
            self.screen.blit(text_surf, (40, 75 + i * 20))
        
        # Área de logs
        pygame.draw.rect(self.screen, (20, 20, 40), (20, 160, self.width - 40, self.height - 200), 0, 5)
        pygame.draw.rect(self.screen, self.colors['border'], (20, 160, self.width - 40, self.height - 200), 2, 5)
        
        # Logs
        y = 175
        for text, color in self.lines:
            text_surf = self.font.render(text, True, color)
            self.screen.blit(text_surf, (40, y))
            y += 20
        
        # Rodapé
        help_text = self.font.render("F1 - Simular discagem | F2 - Simular erro | F3 - Mensagem | ESC - Sair", 
                                   True, self.colors['text'])
        self.screen.blit(help_text, (20, self.height - 30))
        
        pygame.display.flip()
    
    def run(self):
        """Loop principal"""
        clock = pygame.time.Clock()
        running = True
        
        print("🎮 Iniciando teste da interface gráfica...")
        print("🎯 Controles:")
        print("   F1 - Simular discagem")
        print("   F2 - Simular erro")
        print("   F3 - Adicionar mensagem")
        print("   ESC - Sair")
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    
                    elif event.key == pygame.K_F1:
                        self.simular_discagem()
                    
                    elif event.key == pygame.K_F2:
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        self.add_line(f"[{timestamp}] ❌ Erro simulado no processo", self.colors['error'])
                    
                    elif event.key == pygame.K_F3:
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        self.add_line(f"[{timestamp}] 📝 Mensagem de teste #{len(self.lines)}")
            
            self.draw_interface()
            clock.tick(30)
        
        pygame.quit()
        print("✅ Teste concluído!")
        return True

# Executar o teste
if __name__ == "__main__":
    gui = ADACTestGUI()
    gui.run()