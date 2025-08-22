import subprocess
import time

device = "0082825555"  # seu device ID
numero_teste = "0082825555"  # número para testar

print("=== DESCOBRINDO COORDENADAS DO BOTÃO DISCAR ===")

# Preparar ambiente
subprocess.run(f"adb -s {device} shell input keyevent KEYCODE_HOME".split())
subprocess.run(f"adb -s {device} shell am force-stop com.android.dialer".split())
time.sleep(1)

# Abrir discador com número
subprocess.run(f"adb -s {device} shell am start -a android.intent.action.DIAL -d tel:{numero_teste}".split())
time.sleep(3)

print("\n🔍 Agora olhe na tela do celular e identifique onde está o botão verde de discar")
print("📱 As coordenadas são baseadas na resolução da tela (ex: 1080x2400)")
print("💡 O formato é (X, Y) onde X vai de 0-1080, Y vai de 0-2400")

while True:
    try:
        x = input("\nDigite a coordenada X do botão discar: ").strip()
        y = input("Digite a coordenada Y do botão discar: ").strip()
        
        if not x or not y:
            print("Coordenadas inválidas. Tente novamente.")
            continue
        
        print(f"Testando tap em ({x}, {y})...")
        subprocess.run(f"adb -s {device} shell input tap {x} {y}".split())
        
        time.sleep(3)
        
        # Verificar se discou
        result = subprocess.run(
            f"adb -s {device} shell dumpsys telephony.registry".split(),
            capture_output=True, text=True
        )
        
        if "mCallState=2" in result.stdout:
            print("✅✅✅ PERFEITO! Coordenadas corretas encontradas!")
            print(f"Use: ({x}, {y}) no seu código")
            break
        else:
            print("❌ Não discou. Tente outras coordenadas.")
            # Encerrar qualquer tentativa falha
            subprocess.run(f"adb -s {device} shell input keyevent KEYCODE_ENDCALL".split())
            
    except KeyboardInterrupt:
        print("\nSaindo...")
        break
    except Exception as e:
        print(f"Erro: {e}")

# Limpar
subprocess.run(f"adb -s {device} shell input keyevent KEYCODE_ENDCALL".split())
subprocess.run(f"adb -s {device} shell input keyevent KEYCODE_HOME".split())