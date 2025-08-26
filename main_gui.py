#!/usr/bin/env python3
"""
Main com GUI no thread principal
"""

import pygame
import sys
import os
import time
import threading
from datetime import datetime
from gui_integrada import ADACGUI, log_message, update_gui_status

# Variáveis globais para comunicação entre threads
adac_running = False
adac_thread = None

def run_adac(gui):
    """Função que executa o ADAC em thread separada"""
    global adac_running
    
    try:
        # Simular inicialização do ADAC
        log_message("Iniciando ADAC...", "success")
        update_gui_status(status="Verificando dispositivos")
        
        # Aqui você integra com o código real do ADAC
        # Por enquanto, vamos simular
        
        time.sleep(1)
        update_gui_status(device="Conectado: 0082825555")
        
        time.sleep(1)
        update_gui_status(csv="Carregado: contatos.csv", total=5)
        
        # Simular processamento
        for i in range(5):
            if not adac_running:
                break
                
            update_gui_status(
                processados=i,
                sucesso=i,
                current=f"Contato {i+1} - 11999999999",
                status="Discando..."
            )
            
            log_message(f"Discando para contato {i+1}")
            time.sleep(2)
            
            if i % 2 == 0:
                log_message("✅ Chamada atendida!", "success")
            else:
                log_message("❌ Chamada não atendida", "warning")
            
            time.sleep(1)
        
        if adac_running:
            update_gui_status(status="Concluído", processados=5, sucesso=3, falha=2)
            log_message("Processamento concluído!", "success")
            
    except Exception as e:
        log_message(f"Erro no ADAC: {e}", "error")
        update_gui_status(status=f"Erro: {str(e)}")
    finally:
        adac_running = False

def main():
    global adac_running, adac_thread
    
    # Inicializar GUI
    gui = ADACGUI()
    
    # Botões e interface interativa
    start_button_rect = pygame.Rect(50, 500, 150, 40)
    stop_button_rect = pygame.Rect(220, 500, 150, 40)
    
    clock = pygame.time.Clock()
    
    log_message("Sistema inicializado. Clique em Iniciar para começar.", "success")
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                adac_running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    adac_running = False
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button_rect.collidepoint(event.pos) and not adac_running:
                    adac_running = True
                    adac_thread = threading.Thread(target=run_adac, args=(gui,))
                    adac_thread.daemon = True
                    adac_thread.start()
                    log_message("ADAC iniciado!", "success")
                    
                elif stop_button_rect.collidepoint(event.pos) and adac_running:
                    adac_running = False
                    log_message("ADAC interrompido", "warning")
        
        # Desenhar interface
        gui.screen.fill(gui.colors['bg'])
        
        # Desenhar botões
        pygame.draw.rect(gui.screen, gui.colors['success'] if not adac_running else (100, 100, 100), start_button_rect, 0, 5)
        pygame.draw.rect(gui.screen, gui.colors['error'] if adac_running else (100, 100, 100), stop_button_rect, 0, 5)
        
        start_text = gui.font.render("Iniciar ADAC", True, gui.colors['text'])
        stop_text = gui.font.render("Parar ADAC", True, gui.colors['text'])
        
        gui.screen.blit(start_text, (start_button_rect.x + 15, start_button_rect.y + 12))
        gui.screen.blit(stop_text, (stop_button_rect.x + 20, stop_button_rect.y + 12))
        
        # Desenhar o resto da interface
        gui.draw_interface()
        
        pygame.display.flip()
        clock.tick(30)
    
    # Finalizar
    adac_running = False
    if adac_thread and adac_thread.is_alive():
        adac_thread.join(timeout=2.0)
    
    pygame.quit()

if __name__ == "__main__":
    main()