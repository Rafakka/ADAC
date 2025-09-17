import subprocess

def enviar_sms(numero, mensagem):
    """
    Abre o app de SMS no celular com número e texto já preenchidos.
    O usuário só precisa confirmar no celular.
    """
    try:
        comando = [
            "adb", "shell", "am", "start",
            "-a", "android.intent.action.SENDTO",
            "-d", f"sms:{numero}",
            "--es", "sms_body", mensagem,
            "--ez", "exit_on_sent", "true"
        ]
        resultado = subprocess.run(comando, capture_output=True, text=True)
        
        if resultado.returncode == 0:
            print(f"✅ SMS preparado para {numero}: \"{mensagem}\"")
            print("📱 Confirme o envio no celular.")
        else:
            print("❌ Erro ao tentar abrir o app de SMS")
            print(resultado.stderr)
    except Exception as e:
        print(f"⚠️ Erro inesperado: {e}")


# Exemplo de uso:
if __name__ == "__main__":
    enviar_sms("+5511998213035", "Teste de SMS via ADB 🚀")
