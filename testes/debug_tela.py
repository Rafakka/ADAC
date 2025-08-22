import subprocess
import time

device = "0082825555"

print("=== DEBUG DE TELA ===")
print("Vamos capturar a tela e descobrir onde clicar")

# 1. Primeiro, abrir o discador com um número
subprocess.run(f"adb -s {device} shell am start -a android.intent.action.DIAL -d tel:0082825555".split())
time.sleep(3)

# 2. Capturar screenshot e baixar
subprocess.run(f"adb -s {device} shell screencap -p /sdcard/screen.png".split())
subprocess.run(f"adb -s {device} pull /sdcard/screen.png".split())

print("✅ Screenshot salva como screen.png")
print("👀 Abra a imagem e veja onde está o botão verde de discar")

# 3. Obter informações da tela
result = subprocess.run(f"adb -s {device} shell wm size".split(), capture_output=True, text=True)
print(f"📏 Resolução da tela: {result.stdout.strip()}")

result = subprocess.run(f"adb -s {device} shell wm density".split(), capture_output=True, text=True)
print(f"📊 Densidade da tela: {result.stdout.strip()}")

print("\n💡 Use as coordenadas baseadas na resolução real da tela!")