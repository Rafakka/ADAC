import logging
from caller import numero_tem_whatsapp, enviar_whatsapp

# Configurar logger para console
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Lista de números simulados
numeros_teste = [
    {"numero": "11999999999", "tem_whatsapp": True},
    {"numero": "11988888888", "tem_whatsapp": False}
]

# Mensagem de teste
mensagem = "Teste de envio ADAC"

# Loop de teste
for contato in numeros_teste:
    numero = contato["numero"]
    print(f"\n--- Testando número: {numero} ---")
    
    # Simular checagem de WhatsApp (aqui usamos valor do mock)
    # Substitua numero_tem_whatsapp pelo valor do mock
    if contato["tem_whatsapp"]:
        logging.info(f"Mock: {numero} possui WhatsApp")
        sucesso = enviar_whatsapp(numero, mensagem)
        if sucesso:
            logging.info(f"✅ WhatsApp enviado para {numero}")
        else:
            logging.warning(f"❌ Falha ao enviar WhatsApp para {numero}")
    else:
        logging.info(f"Mock: {numero} NÃO possui WhatsApp, deveria enviar SMS")
        # Aqui você pode chamar a função de SMS real se quiser
        logging.info(f"✅ SMS enviado para {numero} (simulado)")
