import pygame
from datetime import datetime
from logger import set_gui

class ADACGUI:
    def __init__(self):
        pygame.init()
        self.width, self.height = 1000, 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("ADAC - Auto Discador")
        
        self.colors = {
            'bg': (0,12,24),
            'text': (180,230,180),
            'error': (255,100,100),
            'success': (100,255,100),
            'warning': (255,255,100),
            'header': (100,200,255),
            'border': (0,80,160),
            'panel': (20,40,60)
        }
        
        self.font = pygame.font.SysFont("Consolas",15)
        self.font_bold = pygame.font.SysFont("Consolas",15,bold=True)
        self.title_font = pygame.font.SysFont("Consolas",24,bold=True)
        
        self.lines = []
        self.max_lines = 25
        self.status = "Inicializando..."
        self.device_status = "Não conectado"
        self.csv_status = "Não carregado"
        self.contatos_total = 0
        self.contatos_processados = 0
        self.contatos_sucesso = 0
        self.contatos_falha = 0
        self.current_contact = "Nenhum"
        self.running = True
        self.paused = False
        
        set_gui(self)  # conecta logger
    
    def add_line(self, text, level="info"):
        if level in ['error','warning','success']:
            timestamp = datetime.now().strftime("%H:%M:%S")
            symbol = {"error":"❌","warning":"⚠️","success":"✅"}[level]
            formatted = f"[{timestamp}] {symbol} {text}"
        else:
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted = f"[{timestamp}] 🔹 {text}"
        
        self.lines.append((formatted, level))
        if len(self.lines) > self.max_lines:
            self.lines = self.lines[-self.max_lines:]
    
    def update_status(self, **kwargs):
        for k,v in kwargs.items():
            if hasattr(self,k):
                setattr(self,k,v)
    
    def draw_interface(self):
        self.screen.fill(self.colors['bg'])
        y = 20
        for text, level in self.lines:
            color = self.colors.get(level,self.colors['text'])
            surf = self.font.render(text,True,color)
            self.screen.blit(surf,(20,y))
            y+=18
        pygame.display.flip()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                self.running=False
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    self.running=False
                elif event.key==pygame.K_SPACE:
                    self.paused=not self.paused
                    self.add_line(f"Discagem {'PAUSADA' if self.paused else 'EXECUTANDO'}", "warning" if self.paused else "success")
                elif event.key==pygame.K_F1:
                    self.add_line("Ajuda: F1=Ajuda | ESPAÇO=Pausar | ESC=Sair", "header")
    
    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            self.handle_events()
            self.draw_interface()
            clock.tick(30)
        pygame.quit()

def init_gui_if_enabled():
    from config import GUI_ENABLED
    if GUI_ENABLED:
        gui = ADACGUI()
        return gui
    return None
