from csv_manager import CSVManager
from caller import discar_e_transferir
from config import CSV_PATH

def main():
    csv_manager =CSVManager(CSV_PATH)
    csv_manager.criar_csv_inicial()
    
    contatos = csv_manager.ler_contatos()

    for contato in contatos:
        numero = contato["numero"]
        print(f"Discando {numero}...")
        discar_e_transferir(numero)

if __name__=="__main__":
    main()