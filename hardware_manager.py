import subprocess
import time as time_module
from config import ADB_PATH
from logger import log_combined

def detectar_dispositivos():
    """Detecta dispositivos Android conectados via ADB"""
    try:
        result = subprocess.run([ADB_PATH,"devices","-l"], capture_output=True, text=True, timeout=10)
        devices = []
        for line in result.stdout.splitlines():
            if "device usb:" in line:
                parts = line.split()
                device_id = parts[0]
                model = next((p.split(":")[1] for p in parts if p.startswith("model:")), "Desconhecido")
                devices.append({"id": device_id, "model": model})
                log_combined(f"Dispositivo detectado: {device_id} ({model})", "success")
        return devices if devices else None
    except Exception as e:
        log_combined(f"Erro ao detectar dispositivos: {e}", "error")
        return None

def esperar_celular_conectar(gui=None):
    """Aguarda conexão do celular"""
    log_combined("🔍 Aguardando conexão do celular...", "warning", gui)
    log_combined("💡 Conecte o celular via USB e ative a depuração USB", "warning", gui)

    try:
        import pygame
        import time as time_module
        clock = pygame.time.Clock()

        while True:
            devices = detectar_dispositivos()
            
            if devices:  # se encontrou pelo menos um dispositivo
                celular_id = devices[0]["id"]
                modelo = devices[0]["model"]
                log_combined(f"✅ Celular detectado: {celular_id} ({modelo})", "success", gui)
                return celular_id  # <--- retorna o ID imediatamente

            # Verifica eventos do usuário
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    log_combined("Operação cancelada pelo usuário", "warning", gui)
                    return None
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    log_combined("Operação cancelada pelo usuário", "warning", gui)
                    return None

            if gui:
                gui.draw_interface()
            
            # Log de waiting a cada 5s
            if int(time_module.time()) % 5 == 0:
                log_combined("⏳ Aguardando conexão do celular...", "warning", gui)

            clock.tick(1)

    except Exception as e:
        log_combined(f"Erro ao aguardar celular: {e}", "error", gui)
        return None

