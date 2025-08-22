import subprocess
import sys
from csv_manager import CSVManager
from caller import discar_e_transferir
from config import ADB_PATH

def main():

    result = subprocess.run([ADB_PATH, "devices"], capture_output=True, text=True)
    devices = [line.split()[0] for line in result.stdout.splitlines() if "\tdevice" in line]

    if not devices:
        print("Nenhum celular detectado. Conecte o celular e habilite a depuração USB.")
        sys.exit(1)

    CELULAR = devices[0]
    print(f"Usando celular: {CELULAR}")

    if len(sys.argv) < 2:
        csv_path = input("Digite o caminho do CSV (ex: /app/contatos/contatos.csv): ")
    else:
        csv_path = sys.argv[1]

    csv_manager =CSVManager(sys.argv)
    csv_manager.criar_csv_inicial()
    
    contatos = csv_manager.ler_contatos()

    for contato in contatos:
        numero = contato["numero"]
        print(f"Discando {numero}...")
        discar_e_transferir(numero)

if __name__=="__main__":
    main()