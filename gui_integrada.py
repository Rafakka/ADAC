import pygame
from datetime import datetime

# Instância global da GUI
gui_instance = None

class ADACGUI:
    def __init__(self):
        pygame.init()
        self.width = 1000
        self.height = 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("ADAC - Auto Discador")

        self.colors = {
            'bg': (0, 12, 24),
            'text': (180, 230, 180),
            'error': (255, 100, 100),
            'success': (100, 255, 100),
            'warning': (255, 255, 100),
            'header': (100, 200, 255),
            'border': (0, 80, 160),
            'panel': (20, 40, 60),
            'highlight': (0, 120, 240)
        }

        self.font = pygame.font.SysFont("Consolas", 15)
        self.font_bold = pygame.font.SysFont("Consolas", 15, bold=True)
        self.title_font = pygame.font.SysFont("Consolas", 24, bold=True)
        self.small_font = pygame.font.SysFont("Consolas", 13)

        self.lines = []
        self.max_lines = 25
        self.status = "Inicializando..."
        self.device_status = "Não conectado"
        self.csv_status = "Não carregado"
        self.contatos_processados = 0
        self.contatos_total = 0
        self.contatos_sucesso = 0
        self.contatos_falha = 0
        self.current_contact = "Nenhum"

        self.running = True
        self.paused = False

        self.init_display()

    def init_display(self):
        self.add_line("═" * 90, 'border')
        self.add_line("    ADAC - AUTO DISCADOR AVANÇADO", 'header')
        self.add_line("═" * 90, 'border')
        self.add_line(f" Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        self.add_line(" Pressione F1 para ajuda, ESPAÇO para pausar, ESC para sair")
        self.add_line("═" * 90, 'border')
        self.add_line("")

    def add_line(self, text, color_name=None, level="info"):
        if level == "error":
            color_val = self.colors['error']
            prefix = "❌"
        elif level == "warning":
            color_val = self.colors['warning']
            prefix = "⚠️"
        elif level == "success":
            color_val = self.colors['success']
            prefix = "✅"
        else:
            color_val = self.colors.get(color_name, self.colors['text'])
            prefix = "🔹"
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_text = f"[{timestamp}] {prefix} {text}"
        self.lines.append((formatted_text, color_val))
        if len(self.lines) > self.max_lines:
            self.lines = self.lines[-self.max_lines:]

    def update_status(self, status=None, device=None, csv=None, 
                     total=None, processados=None, sucesso=None, falha=None,
                     current=None):
        if status: self.status = status
        if device: self.device_status = device
        if csv: self.csv_status = csv
        if total is not None: self.contatos_total = total
        if processados is not None: self.contatos_processados = processados
        if sucesso is not None: self.contatos_sucesso = sucesso
        if falha is not None: self.contatos_falha = falha
        if current: self.current_contact = current

    def draw_interface(self):
        self.screen.fill(self.colors['bg'])
        title = self.title_font.render("ADAC - AUTO DISCADOR", True, self.colors['header'])
        self.screen.blit(title, (20, 15))
        # Painéis
        self.draw_panel(20, 60, self.width - 40, 120, "STATUS DO SISTEMA")
        status_texts = [
            f"Status: {self.status}",
            f"Dispositivo: {self.device_status}",
            f"Arquivo CSV: {self.csv_status}",
            f"Contato atual: {self.current_contact}"
        ]
        for i, text in enumerate(status_texts):
            surf = self.font_bold.render(text, True, self.colors['text'])
            self.screen.blit(surf, (40, 85 + i * 20))
        # Painel estatísticas
        self.draw_panel(20, 200, (self.width - 50) // 2, 100, "ESTATÍSTICAS")
        stats_texts = [
            f"Total: {self.contatos_total} contatos",
            f"Processados: {self.contatos_processados}",
            f"Sucesso: {self.contatos_sucesso}",
            f"Falha: {self.contatos_falha}",
            f"Taxa: {self.calculate_success_rate():.1f}%"
        ]
        for i, text in enumerate(stats_texts):
            surf = self.font.render(text, True, self.colors['text'])
            self.screen.blit(surf, (40, 225 + i * 18))
        # Painel progresso
        self.draw_panel((self.width - 50) // 2 + 30, 200, (self.width - 50) // 2, 100, "PROGRESSO")
        if self.contatos_total > 0:
            progresso = (self.contatos_processados / self.contatos_total) * 100
            bar_width = ((self.width - 150) // 2) * (progresso / 100)
            pygame.draw.rect(self.screen, self.colors['panel'], ((self.width - 50) // 2 + 50, 240, (self.width - 150) // 2, 20), 0, 10)
            pygame.draw.rect(self.screen, self.colors['success'], ((self.width - 50) // 2 + 50, 240, bar_width, 20), 0, 10)
            progress_text = f"{progresso:.1f}% ({self.contatos_processados}/{self.contatos_total})"
            surf = self.font.render(progress_text, True, self.colors['text'])
            self.screen.blit(surf, ((self.width - 50) // 2 + 50 + 10, 243))
        # Logs
        self.draw_panel(20, 320, self.width - 40, self.height - 370, "LOGS EM TEMPO REAL")
        y = 345
        for text, color in self.lines:
            surf = self.font.render(text, True, color)
            self.screen.blit(surf, (40, y))
            y += 18
        # Rodapé
        controls = "F1 - Ajuda | ESPAÇO - Pausar/Continuar | ESC - Sair"
        if self.paused:
            controls += " | [PAUSADO]"
        surf = self.small_font.render(controls, True, self.colors['text'])
        self.screen.blit(surf, (20, self.height - 25))
        pygame.display.flip()

    def draw_panel(self, x, y, width, height, title):
        pygame.draw.rect(self.screen, self.colors['panel'], (x, y, width, height), 0, 8)
        pygame.draw.rect(self.screen, self.colors['border'], (x, y, width, height), 2, 8)
        if title:
            surf = self.font_bold.render(title, True, self.colors['header'])
            self.screen.blit(surf, (x + 10, y + 8))

    def calculate_success_rate(self):
        if self.contatos_processados == 0:
            return 0
        return (self.contatos_sucesso / self.contatos_processados) * 100

def init_gui():
    """Inicializa GUI e retorna instância"""
    global gui_instance
    try:
        gui_instance = ADACGUI()
        return gui_instance
    except Exception as e:
        print(f"Erro ao inicializar GUI: {e}")
        return None

def update_gui_status_safe(**kwargs):
    """Atualiza status na GUI global se estiver inicializada"""
    global gui_instance
    if gui_instance:
        gui_instance.update_status(**kwargs)
