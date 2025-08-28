import pygame
import sys
from datetime import datetime

class CLIGUI:
    def __init__(self, width=800, height=600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("ADAC - Auto Discador")
        
        # Cores
        self.BG_COLOR = (0, 0, 0)  # Preto
        self.TEXT_COLOR = (0, 255, 0)  # Verde
        self.ERROR_COLOR = (255, 0, 0)  # Vermelho
        self.SUCCESS_COLOR = (0, 255, 0)  # Verde
        self.WARNING_COLOR = (255, 255, 0)  # Amarelo
        
        # Fonte
        self.font = pygame.font.SysFont("Courier New", 16)
        self.big_font = pygame.font.SysFont("Courier New", 20, bold=True)
        
        # Buffer de texto
        self.lines = []
        self.max_lines = 25
        
        # Cabeçalho
        self.add_header()
    
    def add_header(self):
        """Adiciona cabeçalho da aplicação"""
        header = [
            "═" * 60,
            "    ADAC - AUTO DISCADOR AVANÇADO",
            "═" * 60,
            f" Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            " Digite 'help' para ver os comandos disponíveis",
            "═" * 60,
            ""
        ]
        for line in header:
            self.add_line(line)
    
    def add_line(self, text, color=None):
        """Adiciona uma linha ao buffer"""
        if color is None:
            color = self.TEXT_COLOR
        
        self.lines.append((text, color))
        
        # Manter apenas as últimas linhas
        if len(self.lines) > self.max_lines:
            self.lines = self.lines[-self.max_lines:]
        
        self.redraw()
    
    def add_log(self, message):
        """Adiciona mensagem de log formatada"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.add_line(f"[{timestamp}] {message}")
    
    def add_success(self, message):
        """Adiciona mensagem de sucesso"""
        self.add_line(f"✅ {message}", self.SUCCESS_COLOR)
    
    def add_error(self, message):
        """Adiciona mensagem de erro"""
        self.add_line(f"❌ {message}", self.ERROR_COLOR)
    
    def add_warning(self, message):
        """Adiciona mensagem de aviso"""
        self.add_line(f"⚠️  {message}", self.WARNING_COLOR)
    
    def redraw(self):
        """Redesenha a tela"""
        self.screen.fill(self.BG_COLOR)
        
        # Desenhar linhas do buffer
        y = 10
        for text, color in self.lines:
            text_surface = self.font.render(text, True, color)
            self.screen.blit(text_surface, (10, y))
            y += 20
        
        # Desenhar prompt
        prompt = "ADAC> "
        prompt_surface = self.font.render(prompt, True, self.TEXT_COLOR)
        self.screen.blit(prompt_surface, (10, self.height - 30))
        
        pygame.display.flip()
    
    def run(self):
        """Loop principal da interface"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            self.redraw()
            pygame.time.delay(50)
        
        pygame.quit()
        sys.exit()

# Versão simples para testes
def test_gui():
    gui = CLIGUI()
    gui.add_log("Sistema inicializado")
    gui.add_success("Dispositivo conectado: 0082825555")
    gui.add_warning("Nenhum arquivo CSV encontrado")
    gui.add_error("Erro ao conectar com dispositivo")
    gui.add_log("Processamento concluído")
    gui.run()

if __name__ == "__main__":
    test_gui()