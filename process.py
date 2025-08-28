
import os
from datetime import datetime

# importa funções utilitárias
from csv_manager import carregar_contatos, salvar_log_csv


def processar_contatos():
    """
    Função principal que orquestra:
    - Carregar contatos
    - Processar cada contato
    - Salvar logs
    """

    print("🔄 Iniciando processamento...")

    # --- 1. Carregar contatos ---
    contatos = carregar_contatos()
    print(f"📂 {len(contatos)} contatos carregados")

    # --- 2. Processar cada contato ---
    for contato in contatos:
        nome = contato.get("nome", "Desconhecido")
        numero = contato.get("numero", "Sem número")

        # Aqui você define a ação principal
        # Exemplo: simular envio de mensagem
        print(f"✉️ Enviando mensagem para {nome} ({numero})...")

        # Suponha que deu certo
        status = "sucesso"

        # --- 3. Salvar log ---
        salvar_log_csv({
            "data_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "nome": nome,
            "numero": numero,
            "status": status
        })

    print("✅ Processamento finalizado!")


if __name__ == "__main__":
    processar_contatos()
