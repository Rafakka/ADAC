import pygame
import sys
import os
from datetime import datetime
import time
import threading
from config import CONTATOS_DIR, LOGS_DIR, CSV_DEFAULT_PATH

class ADACGUI:
    def __init__(self):
        pygame.init()
        self.width = 1000
        self.height = 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("ADAC - Auto Discador")
        
        # Cores
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
        
        # Fontes
        self.font = pygame.font.SysFont("Consolas", 15)
        self.font_bold = pygame.font.SysFont("Consolas", 15, bold=True)
        self.title_font = pygame.font.SysFont("Consolas", 24, bold=True)
        self.small_font = pygame.font.SysFont("Consolas", 13)
        
        # Estado do sistema
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
        
        # Controles
        self.running = True
        self.paused = False
        self.stopped = False
        
        self.init_display()
    
    def init_display(self):
        """Inicializa o display"""
        self.add_line("═" * 90, self.colors['border'])
        self.add_line("    ADAC - AUTO DISCADOR AVANÇADO", self.colors['header'])
        self.add_line("═" * 90, self.colors['border'])
        self.add_line(f" Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        self.add_line(" Pressione F1 para ajuda, ESPAÇO para pausar, ESC para sair")
        self.add_line("═" * 90, self.colors['border'])
        self.add_line("")
    
    def add_line(self, text, color=None, level="info"):
        """Adiciona uma linha ao buffer com formatação"""
        if color is None:
            color = self.colors['text']
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Adicionar ícone baseado no nível
        if level == "error":
            formatted_text = f"[{timestamp}] ❌ {text}"
            color = self.colors['error']
        elif level == "warning":
            formatted_text = f"[{timestamp}] ⚠️  {text}"
            color = self.colors['warning']
        elif level == "success":
            formatted_text = f"[{timestamp}] ✅ {text}"
            color = self.colors['success']
        else:
            formatted_text = f"[{timestamp}] 🔹 {text}"
        
        self.lines.append((formatted_text, color))
        if len(self.lines) > self.max_lines:
            self.lines = self.lines[-self.max_lines:]
    
    def update_status(self, status=None, device=None, csv=None, 
                     total=None, processados=None, sucesso=None, falha=None,
                     current=None):
        """Atualiza as informações de status"""
        if status: self.status = status
        if device: self.device_status = device
        if csv: self.csv_status = csv
        if total is not None: self.contatos_total = total
        if processados is not None: self.contatos_processados = processados
        if sucesso is not None: self.contatos_sucesso = sucesso
        if falha is not None: self.contatos_falha = falha
        if current: self.current_contact = current
    
    def draw_interface(self):
        """Desenha a interface completa"""
        self.screen.fill(self.colors['bg'])
        
        # Título
        title = self.title_font.render("ADAC - AUTO DISCADOR", True, self.colors['header'])
        self.screen.blit(title, (20, 15))
        
        # Painel de status principal
        self.draw_panel(20, 60, self.width - 40, 120, "STATUS DO SISTEMA")
        
        status_texts = [
            f"Status: {self.status}",
            f"Dispositivo: {self.device_status}",
            f"Arquivo CSV: {self.csv_status}",
            f"Contato atual: {self.current_contact}"
        ]
        
        for i, text in enumerate(status_texts):
            text_surf = self.font_bold.render(text, True, self.colors['text'])
            self.screen.blit(text_surf, (40, 85 + i * 20))
        
        # Painel de estatísticas
        self.draw_panel(20, 200, (self.width - 50) // 2, 100, "ESTATÍSTICAS")
        
        stats_texts = [
            f"Total: {self.contatos_total} contatos",
            f"Processados: {self.contatos_processados}",
            f"Sucesso: {self.contatos_sucesso}",
            f"Falha: {self.contatos_falha}",
            f"Taxa: {self.calculate_success_rate()}%"
        ]
        
        for i, text in enumerate(stats_texts):
            text_surf = self.font.render(text, True, self.colors['text'])
            self.screen.blit(text_surf, (40, 225 + i * 18))
        
        # Painel de progresso
        self.draw_panel((self.width - 50) // 2 + 30, 200, (self.width - 50) // 2, 100, "PROGRESSO")
        
        if self.contatos_total > 0:
            progresso = (self.contatos_processados / self.contatos_total) * 100
            pygame.draw.rect(self.screen, self.colors['panel'], ( (self.width - 50) // 2 + 50, 240, (self.width - 150) // 2, 20), 0, 10)
            pygame.draw.rect(self.screen, self.colors['success'], ( (self.width - 50) // 2 + 50, 240, ((self.width - 150) // 2) * (progresso / 100), 20), 0, 10)
            
            progress_text = f"{progresso:.1f}% ({self.contatos_processados}/{self.contatos_total})"
            text_surf = self.font.render(progress_text, True, self.colors['text'])
            self.screen.blit(text_surf, ((self.width - 50) // 2 + 50 + 10, 243))
        
        # Área de logs
        self.draw_panel(20, 320, self.width - 40, self.height - 370, "LOGS EM TEMPO REAL")
        
        # Logs
        y = 345
        for text, color in self.lines:
            text_surf = self.font.render(text, True, color)
            self.screen.blit(text_surf, (40, y))
            y += 18
        
        # Rodapé com controles
        controls = "F1 - Ajuda | ESPAÇO - Pausar/Continuar | ESC - Sair"
        if self.paused:
            controls += " | [PAUSADO]"
        
        control_text = self.small_font.render(controls, True, self.colors['text'])
        self.screen.blit(control_text, (20, self.height - 25))
        
        pygame.display.flip()
    
    def draw_panel(self, x, y, width, height, title):
        """Desenha um painel com título"""
        pygame.draw.rect(self.screen, self.colors['panel'], (x, y, width, height), 0, 8)
        pygame.draw.rect(self.screen, self.colors['border'], (x, y, width, height), 2, 8)
        
        if title:
            title_text = self.font_bold.render(title, True, self.colors['header'])
            self.screen.blit(title_text, (x + 10, y + 8))
    
    def calculate_success_rate(self):
        """Calcula taxa de sucesso"""
        if self.contatos_processados == 0:
            return 0
        return (self.contatos_sucesso / self.contatos_processados) * 100
    
    def show_help(self):
        """Mostra tela de ajuda"""
        help_lines = [
            "═" * 90,
            "COMANDOS DA INTERFACE:",
            "═" * 90,
            "F1       - Mostrar esta ajuda",
            "ESPAÇO   - Pausar/Continuar discagem",
            "ESC      - Sair do programa",
            "",
            "STATUS DOS ÍCONES:",
            "✅       - Sucesso/Ação concluída",
            "❌       - Erro/Falha",
            "⚠️       - Aviso/Alerta",
            "🔹       - Informação normal",
            "📞       - Discagem em andamento",
            "═" * 90
        ]
        
        for line in help_lines:
            self.add_line(line, self.colors['header'], "info")
    
    def handle_events(self):
        """Processa eventos da interface"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return False
                
                elif event.key == pygame.K_F1:
                    self.show_help()
                
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                    status = "PAUSADO" if self.paused else "EXECUTANDO"
                    self.add_line(f"Discagem {status}", "warning" if self.paused else "success")
        
        return True
    
    def run(self):
        """Loop principal da interface"""
        clock = pygame.time.Clock()
        
        self.add_line("Interface gráfica inicializada", "success")
        self.update_status("Pronto", "Aguardando conexão", "Aguardando CSV")
        
        while self.running:
            if not self.handle_events():
                break
            
            self.draw_interface()
            clock.tick(30)
        
        pygame.quit()
        return not self.stopped

# Instância global para acesso fácil
gui_instance = None

def init_gui():
    """Inicializa a interface gráfica"""
    global gui_instance
    try:
        gui_instance = ADACGUI()
        return gui_instance
    except Exception as e:
        print(f"Erro ao inicializar GUI: {e}")
        return None

def log_message(message, level="info"):
    """Adiciona mensagem à GUI"""
    global gui_instance
    if gui_instance:
        gui_instance.add_line(message, level=level)
    else:
        print(f"[{level.upper()}] {message}")

def update_gui_status(**kwargs):
    """Atualiza status na GUI"""
    global gui_instance
    if gui_instance:
        gui_instance.update_status(**kwargs)

def is_gui_paused():
    """Verifica se a GUI está pausada"""
    global gui_instance
    return gui_instance and gui_instance.paused

def should_stop():
    """Verifica se deve parar execução"""
    global gui_instance
    return gui_instance and not gui_instance.running