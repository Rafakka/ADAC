
import subprocess
import time as time_module

from config import ADB_PATH
from gui_integrada import update_gui_status
from logger import log_combined


def detectar_dispositivos():
    """Detecta dispositivos Android - NÃO USA sys.exit()"""
    try:
        result = subprocess.run([ADB_PATH, "devices", "-l"], capture_output=True, text=True, timeout=30)
        devices = []
        
        for line in result.stdout.splitlines():
            if "device usb:" in line:
                device_id = line.split()[0]
                devices.append(device_id)
                log_combined(f"Dispositivo detectado: {line}", "success")
        
        return devices if devices else None
        
    except Exception as e:
        log_combined(f"Erro ao detectar dispositivos: {e}", "error")
        return None  # Retorna None, não sai do programa


def esperar_celular_conectar(gui=None):
    """Aguarda até que um celular seja conectado ou ESC seja pressionado"""
    global GUI_AVAILABLE
    
    log_combined("🔍 Aguardando conexão do celular...", "warning")
    log_combined("💡 Conecte o celular via USB e ative a depuração USB", "warning")
    
    if GUI_AVAILABLE and gui:
        update_gui_status(
            status="Aguardando celular",
            device="Não conectado",
            current="Conecte o celular e ative depuração USB"
        )
    
    # Configurar pygame para detectar ESC
    try:
        import pygame
        clock = pygame.time.Clock()
        waiting = True
        
        while waiting:
            # Verificar se celular foi conectado
            devices = detectar_dispositivos()
            if devices:
                log_combined(f"✅ Celular detectado: {devices[0]}", "success")
                return devices[0]  # Retorna o ID do dispositivo
            
            # Verificar se usuário pressionou ESC
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    log_combined("Operação cancelada pelo usuário", "warning")
                    return None
            
            # Atualizar interface
            if GUI_AVAILABLE and gui and hasattr(gui, 'draw_interface'):
                gui.draw_interface()
            
            # Mensagem de waiting a cada 5 segundos
            if int(time_module.time()) % 5 == 0:
                log_combined("⏳ Aguardando conexão do celular...", "warning")
            
            clock.tick(1)  # Verificar a cada segundo
            
    except Exception as e:
        log_combined(f"Erro ao aguardar celular: {e}", "error")
        return None
