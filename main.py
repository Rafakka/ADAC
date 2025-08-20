from csv_manager import CSVManager
from csv_manager import registrar_tentativa
from adac import ADAC
from datetime import datetime
from config import CSV_PATH
from caller import discar_e_transferir
import os

def main():
    csv_manager =CSVManager(CSV_PATH)

    if not os.path.exists(CSV_PATH):
        csv_manager.criar_csv_inicial()
        print(f"CSV criado em {CSV_PATH} com cabeçalho inicial.")
    
    contatos = csv_manager.ler_contatos()
    print(f"{len(contatos)} contatos carregados para discagem.")

    adac = ADAC()

    for contato in contatos:
        numero = contato["numero"]
        print(f"Discando {numero}...")

        atendeu = adac.discar_e_transferir(numero)
        