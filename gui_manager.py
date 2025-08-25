import pygame
import sys
import os
import logging
from datetime import datetime
from config import CONTATOS_DIR, LOGS_DIR

class ADACGUI:
    def __init__(self):
        pygame.init()
        self.width = 900
        self.height = 700
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("ADAC - Auto Discador")
        
        # Cores
        self.colors = {
            'bg': (0, 12, 24),  # Azul muito escuro
            'text': (0, 255, 0),  # Verde
            'error': (255, 50, 50),  # Vermelho
            'success': (50, 255, 50),  # Verde
            'warning': (255, 255, 0),  # Amarelo
            'header': (0, 150, 255),  # Azul
            'border': (0, 80, 160)  # Azul mais escuro
        }
        
        # Fontes
        self.font = pygame.font.SysFont("Consolas", 16)
        self.big_font = pygame.font.SysFont("Consolas", 20, bold=True)
        self.title_font = pygame.font.SysFont("Consolas", 24, bold=True)
        
        # Buffer de texto
        self.lines = []
        self.max_lines = 20
        
        # Status
        self.status = "Pronto"
        self.device_status = "Não conectado"
        self.csv_status = "Não carregado"
        
        self.init_display()
    
    def init_display(self):
        """Inicializa o display"""
        self.add_line("═" * 80, self.colors['border'])
        self.add_line("    ADAC - AUTO DISCADOR AVANÇADO", self.colors['header'])
        self.add_line("═" * 80, self.colors['border'])
        self.add_line(f" Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        self.add_line(" Pressione F1 para ajuda")
        self.add_line("═" * 80, self.colors['border'])
        self.add_line("")
    
    def add_line(self, text, color=None):
        """Adiciona uma linha ao buffer"""
        if color is None:
            color = self.colors['text']
        
        self.lines.append((text, color))
        if len(self.lines) > self.max_lines:
            self.lines = self.lines[-self.max_lines:]
    
    def log_message(self, message, level="info"):
        """Adiciona mensagem de log com nível"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if level == "error":
            self.add_line(f"[{timestamp}] ❌ {message}", self.colors['error'])
        elif level == "warning":
            self.add_line(f"[{timestamp}] ⚠️  {message}", self.colors['warning'])
        elif level == "success":
            self.add_line(f"[{timestamp}] ✅ {message}", self.colors['success'])
        else:
            self.add_line(f"[{timestamp}] 🔹 {message}")
    
    def update_status(self, status=None, device=None, csv=None):
        """Atualiza informações de status"""
        if status: self.status = status
        if device: self.device_status = device
        if csv: self.csv_status = csv
    
    def draw_interface(self):
        """Desenha a interface completa"""
        self.screen.fill(self.colors['bg'])
        
        # Desenhar cabeçalho
        title = self.title_font.render("ADAC - AUTO DISCADOR", True, self.colors['header'])
        self.screen.blit(title, (20, 15))
        
        # Desenhar painel de status
        pygame.draw.rect(self.screen, (30, 30, 50), (20, 60, self.width - 40, 80), 0, 5)
        pygame.draw.rect(self.screen, self.colors['border'], (20, 60, self.width - 40, 80), 2, 5)
        
        status_text = [
            f"Status: {self.status}",
            f"Dispositivo: {self.device_status}",
            f"CSV: {self.csv_status}"
        ]
        
        for i, text in enumerate(status_text):
            text_surf = self.font.render(text, True, self.colors['text'])
            self.screen.blit(text_surf, (40, 75 + i * 25))
        
        # Desenhar área de logs
        pygame.draw.rect(self.screen, (20, 20, 40), (20, 160, self.width - 40, self.height - 200), 0, 5)
        pygame.draw.rect(self.screen, self.colors['border'], (20, 160, self.width - 40, self.height - 200), 2, 5)
        
        # Desenhar logs
        y = 175
        for text, color in self.lines:
            text_surf = self.font.render(text, True, color)
            self.screen.blit(text_surf, (40, y))
            y += 20
        
        # Desenhar rodapé
        help_text = self.font.render("F1 - Ajuda | F2 - Status | ESC - Sair", True, self.colors['text'])
        self.screen.blit(help_text, (20, self.height - 30))
        
        pygame.display.flip()
    
    def show_help(self):
        """Mostra tela de ajuda"""
        help_lines = [
            "═" * 80,
            "COMANDOS DISPONÍVEIS:",
            "═" * 80,
            "F1 - Mostrar esta ajuda",
            "F2 - Mostrar status do sistema",
            "F3 - Ver dispositivos conectados",
            "F4 - Carregar CSV",
            "F5 - Iniciar discagem",
            "F6 - Parar discagem",
            "ESC - Sair do programa",
            "═" * 80
        ]
        
        for line in help_lines:
            self.add_line(line, self.colors['header'])
    
    def run(self):
        """Loop principal"""
        running = True
        clock = pygame.time.Clock()
        
        self.log_message("Interface inicializada", "success")
        self.update_status("Pronto", "Aguardando conexão", "Aguardando CSV")
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_F1:
                        self.show_help()
                    elif event.key == pygame.K_F2:
                        self.log_message("Sistema operacional", "info")
                    elif event.key == pygame.K_F5:
                        self.log_message("Iniciando discagem...", "success")
            
            self.draw_interface()
            clock.tick(30)
        
        pygame.quit()
        return True

# Interface simplificada para integração
def start_gui():
    """Inicia a interface gráfica"""
    try:
        gui = ADACGUI()
        return gui.run()
    except Exception as e:
        print(f"Erro na interface: {e}")
        return False

if __name__ == "__main__":
    start_gui()