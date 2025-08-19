import csv
from config import CSV_PATH

def ler_contatos():
    with open(CSV_PATH, newline='') as f:
        return list(csv.DictReader(f))

def atualizar_status(numero, status):
    contatos = ler_contatos()
    for contato in contatos:
        if contato['numero'] == numero:
            contato['status'] = status
            with open(CSV_PATH, 'w', newline='') as f:
                writer =csv.DictWriter(f, fieldnames=['numero','status'])
                writer.writeheader()
                writer.writerows(contatos)