import subprocess
import time
from config import ADB_PATH
from logger import log_combined
from gui_manager import update_gui_status_safe, should_stop

def detectar_dispositivos():
    """
    Detecta dispositivos Android conectados via ADB.
    Retorna lista de IDs ou None se nenhum dispositivo.
    Não usa sys.exit().
    """
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
        return None

def esperar_celular_conectar(gui=None):
    """
    Aguarda até que um celular seja conectado ou ESC seja pressionado.
    Atualiza a GUI se gui estiver presente.
    Retorna o ID do celular conectado ou None se cancelado.
    """
    log_combined("🔍 Aguardando conexão do celular...", "warning")
    log_combined("💡 Conecte o celular via USB e ative a depuração USB", "warning")

    # Atualiza status da GUI
    if gui:
        update_gui_status_safe(status="Aguardando celular", device="Não conectado", current="Conecte o celular e ative depuração USB")

    try:
        import pygame
        clock = pygame.time.Clock()
        waiting = True

        while waiting:
            # Se a GUI sinalizar para parar, encerra
            if should_stop():
                log_combined("Operação cancelada pela GUI", "warning")
                return None

            # Verifica dispositivos
            devices = detectar_dispositivos()
            if devices:
                log_combined(f"✅ Celular detectado: {devices[0]}", "success")
                if gui:
                    update_gui_status_safe(device=devices[0], status="Celular conectado")
                return devices[0]

            # Verifica eventos de teclado no pygame
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    log_combined("Operação cancelada pelo usuário", "warning")
                    return None

            # Atualiza interface
            if gui and hasattr(gui, 'draw_interface'):
                gui.draw_interface()

            # Log de espera a cada 5 segundos
            if int(time.time()) % 5 == 0:
                log_combined("⏳ Aguardando conexão do celular...", "warning")

            clock.tick(1)  # Loop a cada segundo

    except Exception as e:
        log_combined(f"Erro ao aguardar celular: {e}", "error")
        return None
