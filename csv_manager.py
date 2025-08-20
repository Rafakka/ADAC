import csv
from datetime import datetime
from pathlib import Path
from config import CSV_PATH

class CSVManager:
    def __init__(self, path=CSV_PATH):
        self.path = Path(path)

def criar_csv_inicial(self,headers=["numero","status","ultima_tentativa"]):
    if not self.path.exist():
        with open(self.path,"w",newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

def ler_contatos(self):
    if not self.path.exists():
        return[]
    with open(self.path, newline="") as f:
        return list(csv.DictReader(f))

def registrar_tentativa(self, numero,status):
    timestamp = datetime.now().strftime("%H:%M dia %d/%m/%y")
    linhas = []

    if self.path.exists():
        with open(self.path,"r",newline="") as f:
            reader =csv.DictReader(f)
            for row in reader:
                linhas.append(row)
        encontrado = False
        for row in linhas:
            if row["numero"]==numero:
                row["status"]==status
                row["ultima_tentativa"]==timestamp
                encontrado = True
                break
                
            if not encontrado:
                linhas.append({"numero":numero,"status":status,"ultima_tentativa":timestamp})
                
                with open(self.path,"w",newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=["numero","status","ultima_tentativa"])
                    writer.writeheader()
                    writer.writerows(linhas)