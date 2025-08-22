import subprocess
import time

device = "0082825555"
numero_teste = "0082825555"

print("🚀 Testando método eficaz...")

# Testar o comando que funciona
result = subprocess.run([
    "adb", "-s", device, "shell", "am", "start", 
    "-a", "android.intent.action.CALL", 
    "-d", f"tel:{numero_teste}"
], capture_output=True, text=True)

print(f"✅ Comando executado: {result.returncode == 0}")
print(f"📋 Saída: {result.stdout}")
if result.stderr:
    print(f"❌ Erros: {result.stderr}")

# Verificar estado da chamada após 5 segundos
time.sleep(5)
result = subprocess.run([
    "adb", "-s", device, "shell", "dumpsys", "telephony.registry"
], capture_output=True, text=True)

print("📞 Estado da chamada:")
print(result.stdout)

if "mCallState=2" in result.stdout:
    print("🎉 CHAMADA ATIVA! Tudo funcionando!")
    
    # Testar transferência
    subprocess.run(["adb", "-s", device, "shell", "input", "keyevent", "KEYCODE_CALL"])
    time.sleep(3)
    subprocess.run(["adb", "-s", device, "shell", "input", "keyevent", "KEYCODE_ENDCALL"])
    print("✅ Transferência testada!")
else:
    print("❌ Chamada não estabelecida")