import subprocess

device = "0082825555"  # use seu device ID

# Testar keycodes comuns para home
keycodes = [
    "KEYCODE_HOME",
    "KEYCODE_ASSIST",  # às vezes funciona como home
    "KEYCODE_BACK",    # pode ser necessário dar back várias vezes
    "KEYCODE_APP_SWITCH"  # trocar de app
]

for keycode in keycodes:
    print(f"Testando {keycode}...")
    result = subprocess.run([
        "adb", "-s", device, "shell", "input", "keyevent", keycode
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {keycode} funcionou!")
    else:
        print(f"❌ {keycode} falhou: {result.stderr}")
    
    input("Pressione Enter para testar próximo keycode...")