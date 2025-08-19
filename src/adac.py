import csv
import subprocess
import time
import os
import sys

ADB_PATH = "/usr/bin/adb"
TELEFONE_TRANSFERENCIA = "555199999999"

# Pede ao usuário o caminho do CSV
if len(sys.argv) < 2:
    csv_path = input("Digite o caminho do CSV (ex: /app/contatos/contatos.csv): ")
else:
    csv_path = sys.argv[1]

# Detecta automaticamente celulares conectados
result = subprocess.run([ADB_PATH, "devices"], capture_output=True, text=True)
devices = [line.split()[0] for line in result.stdout.splitlines() if "\tdevice" in line]

if not devices:
    print("Nenhum celular detectado. Conecte o celular e habilite a depuração USB.")
    sys.exit(1)

CELULAR = devices[0]
print(f"Usando celular: {CELULAR}")

# Lê contatos
with open(csv_path, newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    contatos = list(reader)

def discar(numero):
    cmd = [ADB_PATH, "-s", CELULAR, "shell", "am", "start",
           "-a", "android.intent.action.CALL", "-d", f"tel:{numero}"]
    subprocess.run(cmd)
    print(f"Discando: {numero}")
    time.sleep(10)
    atendido = True  # Pode evoluir com lógica real
    return atendido

def transferir(numero_transferencia):
    cmd = [ADB_PATH, "-s", CELULAR, "shell", "am", "start",
           "-a", "android.intent.action.CALL", "-d", f"tel:{numero_transferencia}"]
    subprocess.run(cmd)
    print(f"Transferindo ligação para: {numero_transferencia}")
    time.sleep(5)

# Processa ligações
for contato in contatos:
    numero = contato["numero"]
    atendido = discar(numero)
    if atendido:
        transferir(TELEFONE_TRANSFERENCIA)
        contato["status"] = "Atendido e transferido"
    else:
        contato["status"] = "Não atendido"

# Atualiza CSV
with open(csv_path, "w", newline="") as csvfile:
    fieldnames = ["numero", "status"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for contato in contatos:
        writer.writerow(contato)

print("Execução finalizada.")