import pygame
import sys
import os
from datetime import datetime
import time
import logging

class ADACGUI:
    def __init__(self):
        pygame.init()
        self.width = 1000
        self.height = 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        self._log_buffer = []
        pygame.display.set_caption("ADAC - Auto Discador")
        
        # Cores (valores RGB)
        self.colors = {
            'bg': (0, 12, 24),
            'text': (180, 230, 180),
            'error': (255, 100, 100),
            'success': (100, 255, 100),
            'warning': (255, 255, 100),
            'header': (100, 200, 255),
            'border': (0, 80, 160),
            'panel': (20, 40, 60),
            'highlight': (0, 120, 240),
            'scrollbar': (100, 100, 100),
            'scrollbar_active': (150, 150, 150)
        }
        
        # Fontes
        self.font = pygame.font.SysFont("Consolas", 15)
        self.font_bold = pygame.font.SysFont("Consolas", 15, bold=True)
        self.title_font = pygame.font.SysFont("Consolas", 24, bold=True)
        self.small_font = pygame.font.SysFont("Consolas", 13)
        
        # Estado do sistema
        self.lines = []
        self.all_lines = []  # Todas as linhas (para scroll)
        self.max_visible_lines = 20  # Linhas visíveis na tela
        self.scroll_offset = 0  # Offset do scroll
        self.scrollbar_dragging = False
        
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
        
        self.init_display()
    
    def init_display(self):
        """Inicializa o display"""
        self.add_line("═" * 90, 'border')
        self.add_line("    ADAC - AUTO DISCADOR AVANÇADO", 'header')
        self.add_line("═" * 90, 'border')
        self.add_line(f" Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        self.add_line(" Pressione F1 para ajuda, ESPAÇO para pausar, ESC para sair")
        self.add_line("═" * 90, 'border')
        self.add_line("")
    
    def add_line(self, text, color_name=None, level="info"):
        """Adiciona uma linha ao buffer com formatação"""
        # Determinar cor baseada no nível ou nome da cor
        if level == "error":
            color_val = self.colors['error']
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_text = f"[{timestamp}] ❌ {text}"
            logging.error(text)    
        elif level == "warning":
            color_val = self.colors['warning']
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_text = f"[{timestamp}] ⚠️  {text}"
            logging.warning(text)
        elif level == "success":
            color_val = self.colors['success']
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_text = f"[{timestamp}] ✅ {text}"
        else:
            # Usar cor pelo nome ou padrão
            if color_name and color_name in self.colors:
                color_val = self.colors[color_name]
            else:
                color_val = self.colors['text']
                logging.info(text)
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_text = f"[{timestamp}] 🔹 {text}"
        self.all_lines.append((formatted_text, color_val))
        self._update_visible_lines()
    
    def _update_visible_lines(self):
        """Atualiza as linhas visíveis baseadas no scroll offset"""
        start_idx = max(0, len(self.all_lines) - self.max_visible_lines - self.scroll_offset)
        end_idx = len(self.all_lines) - self.scroll_offset
        self.lines = self.all_lines[start_idx:end_idx]
    
    def handle_scroll(self, event):
        """Manipula eventos de scroll do mouse"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                self.scroll_offset = max(0, self.scroll_offset - 3)
            elif event.button == 5:  # Scroll down
                max_scroll = max(0, len(self.all_lines) - self.max_visible_lines)
                self.scroll_offset = min(max_scroll, self.scroll_offset + 3)
            elif event.button == 1:  # Botão esquerdo - arrastar scrollbar
                scrollbar_rect = self._get_scrollbar_rect()
                if scrollbar_rect.collidepoint(event.pos):
                    self.scrollbar_dragging = True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.scrollbar_dragging = False
        
        elif event.type == pygame.MOUSEMOTION and self.scrollbar_dragging:
            self._handle_scrollbar_drag(event)
        
        self._update_visible_lines()
    
    def _get_scrollbar_rect(self):
        """Retorna o retângulo da scrollbar"""
        if len(self.all_lines) <= self.max_visible_lines:
            return None
        
        total_lines = len(self.all_lines)
        visible_ratio = self.max_visible_lines / total_lines
        scrollbar_height = int((self.height - 370) * visible_ratio)
        
        scrollable_lines = total_lines - self.max_visible_lines
        scroll_pos_ratio = self.scroll_offset / scrollable_lines if scrollable_lines > 0 else 0
        
        scrollbar_y = 320 + int((self.height - 370 - scrollbar_height) * scroll_pos_ratio)
        
        return pygame.Rect(self.width - 20, scrollbar_y, 10, scrollbar_height)
    
    def _handle_scrollbar_drag(self, event):
        """Manipula arraste da scrollbar"""
        if len(self.all_lines) <= self.max_visible_lines:
            return
        
        total_lines = len(self.all_lines)
        scrollable_lines = total_lines - self.max_visible_lines
        
        # Calcular posição baseada no mouse
        mouse_y_relative = event.pos[1] - 320
        total_scroll_area = self.height - 370
        scroll_ratio = max(0, min(1, mouse_y_relative / total_scroll_area))
        
        self.scroll_offset = int(scrollable_lines * scroll_ratio)
    
    def draw_interface(self):
        """Desenha a interface completa com scroll"""
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
            bar_width = ((self.width - 150) // 2) * (progresso / 100)
            pygame.draw.rect(self.screen, self.colors['panel'], ((self.width - 50) // 2 + 50, 240, (self.width - 150) // 2, 20), 0, 10)
            pygame.draw.rect(self.screen, self.colors['success'], ((self.width - 50) // 2 + 50, 240, bar_width, 20), 0, 10)
            
            progress_text = f"{progresso:.1f}% ({self.contatos_processados}/{self.contatos_total})"
            text_surf = self.font.render(progress_text, True, self.colors['text'])
            self.screen.blit(text_surf, ((self.width - 50) // 2 + 50 + 10, 243))
        
        # Área de logs
        self.draw_panel(20, 320, self.width - 40, self.height - 370, "LOGS EM TEMPO REAL")
        
        # Logs com scroll
        y = 345
        for text, color in self.lines:
            text_surf = self.font.render(text, True, color)
            self.screen.blit(text_surf, (40, y))
            y += 18
        
        # Desenhar scrollbar se necessário
        self._draw_scrollbar()
        
        # Rodapé com controles
        controls = "F1 - Ajuda | Mouse Scroll - Navegar | ESC - Sair"
        if self.paused:
            controls += " | [PAUSADO]"
        
        control_text = self.small_font.render(controls, True, self.colors['text'])
        self.screen.blit(control_text, (20, self.height - 25))
        
        pygame.display.flip()
    
    def _draw_scrollbar(self):
        """Desenha a scrollbar"""
        if len(self.all_lines) <= self.max_visible_lines:
            return
        
        scrollbar_rect = self._get_scrollbar_rect()
        if scrollbar_rect:
            pygame.draw.rect(self.screen, self.colors['scrollbar_active'] if self.scrollbar_dragging else self.colors['scrollbar'], scrollbar_rect, 0, 3)
    
    def handle_events(self):
        """Processa eventos da interface incluindo scroll"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False
            
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                self.handle_scroll(event)
            
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
        """Desenha a interface completa com scroll"""
        self.screen.fill(self.colors['bg'])
        
        # Título
        title = self.title_font.render("ADAC - AUTO DISCADOR", True, self.colors['header'])
        self.screen.blit(title, (20, 15))
        
        # Painel de status principal - COM LARGURA FIXA
        panel_width = self.width - 40
        self.draw_panel(20, 60, panel_width, 120, "STATUS DO SISTEMA")
        
        status_texts = [
            f"Status: {self.status}",
            f"Dispositivo: {self.device_status}",
            f"Arquivo CSV: {self.csv_status}",
            f"Contato atual: {self.current_contact}"
        ]
        
        for i, text in enumerate(status_texts):
            # Cortar texto se for muito longo
            if len(text) > 80:
                text = text[:77] + "..."
            text_surf = self.font_bold.render(text, True, self.colors['text'])
            self.screen.blit(text_surf, (40, 85 + i * 20))
        
        # Painel de estatísticas - COM LARGURA CONTROLADA
        stats_width = (self.width - 50) // 2
        self.draw_panel(20, 200, stats_width, 100, "ESTATÍSTICAS")
        
        stats_texts = [
            f"Total: {self.contatos_total}",
            f"Processados: {self.contatos_processados}",
            f"Sucesso: {self.contatos_sucesso}",
            f"Falha: {self.contatos_falha}",
            f"Taxa: {self.calculate_success_rate()}%"
        ]
        
        for i, text in enumerate(stats_texts):
            text_surf = self.font.render(text, True, self.colors['text'])
            self.screen.blit(text_surf, (40, 225 + i * 18))
        
        # Painel de progresso
        progress_width = (self.width - 50) // 2
        self.draw_panel(stats_width + 30, 200, progress_width, 100, "PROGRESSO")
        
        if self.contatos_total > 0:
            progresso = (self.contatos_processados / self.contatos_total) * 100
            bar_max_width = progress_width - 100  # Largura máxima da barra
            bar_width = max(10, min(bar_max_width, bar_max_width * (progresso / 100)))
            
            pygame.draw.rect(self.screen, self.colors['panel'], (stats_width + 50, 240, bar_max_width, 20), 0, 10)
            pygame.draw.rect(self.screen, self.colors['success'], (stats_width + 50, 240, bar_width, 20), 0, 10)
            
            progress_text = f"{progresso:.1f}% ({self.contatos_processados}/{self.contatos_total})"
            text_surf = self.font.render(progress_text, True, self.colors['text'])
            self.screen.blit(text_surf, (stats_width + 60, 243))
        
        # Área de logs
        self.draw_panel(20, 320, self.width - 40, self.height - 370, "LOGS EM TEMPO REAL")
        
        # Logs com scroll - garantir que não ultrapassem a largura
        y = 345
        for text, color in self.lines:
            # Cortar texto muito longo
            if len(text) > 120:
                text = text[:117] + "..."
            text_surf = self.font.render(text, True, color)
            self.screen.blit(text_surf, (40, y))
            y += 18
        
        # Desenhar scrollbar se necessário
        self._draw_scrollbar()
        
        # Rodapé com controles - texto cortado se necessário
        controls = "F1 - Ajuda | Mouse Scroll - Navegar | ESC - Sair"
        if self.paused:
            controls += " | [PAUSADO]"
        
        if len(controls) > 100:
            controls = controls[:97] + "..."
        
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
            self.add_line(line, 'header')
    
    def handle_events(self):
        """Processa eventos da interface"""
        try:
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
        except pygame.error:
            self.running = False
            return False
    
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
        return True

    def log_message(message, level="info"):
        global gui_instance
        if gui_instance:
            try:
                gui_instance.add_line(message, level=level)
            except Exception as e:
                logging.error(f"Erro ao logar na GUI: {e}")
                
    def keep_alive_until_escape(self, message="Processamento concluído"):
        """Mantém a janela aberta até o usuário pressionar ESC"""
        self.add_line("")
        self.add_line("═" * 90, 'border')
        self.add_line(f"🎯 {message}", 'success')
        self.add_line("💡 Pressione ESC para fechar a janela", 'header')
        self.add_line("═" * 90, 'border')
        
        clock = pygame.time.Clock()
        waiting = True
        
        while waiting and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        waiting = False
                        self.running = False
            
            # Atualizar display
            self.draw_interface()
            clock.tick(30)

    def wait_for_escape_safe(self):
        """Aguarda ESC de forma segura, evitando erros X11"""
        self.add_line("═" * 60, 'border')
        self.add_line("🎯 PROCESSAMENTO CONCLUÍDO", 'success')
        self.add_line("💡 Pressione ESC para fechar", 'header')
        self.add_line("═" * 60, 'border')
        
        clock = pygame.time.Clock()
        waiting = True
        
        while waiting and self.running:
            try:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        waiting = False
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            waiting = False
                            self.running = False
                
                self.draw_interface()
                clock.tick(30)
                
            except pygame.error as e:
                if "X Error" in str(e) or "MIT-SHM" in str(e):
                    # Ignorar erro e continuar
                    continue
                else:
                    # Outro erro, parar
                    waiting = False
                    break        
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

def safe_quit(self):
    """Fechamento seguro que evita segmentation fault"""
    self.running = False
    # Não chame pygame.quit() aqui - deixe o PyGame lidar com isso