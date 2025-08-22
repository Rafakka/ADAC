import subprocess
import time

device = "0082825555"

def testar_area(x_inicio, x_fim, y_inicio, y_fim, passo=50):
    """Testa taps em uma área da tela"""
    print(f"🔍 Varrendo área: X({x_inicio}-{x_fim}) Y({y_inicio}-{y_fim})")
    
    for y in range(y_inicio, y_fim + 1, passo):
        for x in range(x_inicio, x_fim + 1, passo):
            print(f"Testando ({x}, {y})...")
            
            # Fazer tap
            subprocess.run(f"adb -s {device} shell input tap {x} {y}".split())
            time.sleep(2)
            
            # Verificar se discou
            result = subprocess.run(
                f"adb -s {device} shell dumpsys telephony.registry".split(),
                capture_output=True, text=True
            )
            
            if "mCallState=2" in result.stdout:
                print(f"🎯 ENCONTRADO! Coordenadas: ({x}, {y})")
                return (x, y)
            else:
                # Cancelar se discou algo errado
                subprocess.run(f"adb -s {device} shell input keyevent KEYCODE_ENDCALL".split())
    
    return None

# Executar varredura
coordenadas = testar_area(400, 700, 1900, 2100, 50)
if coordenadas:
    print(f"✅ Botão encontrado em: {coordenadas}")
else:
    print("❌ Botão não encontrado na área varrida")