import subprocess
from tracker import foi_atendido
from config import CELULAR, NUMERO_TRANSFER

class Caller:
    def __init__(self, csv_manager):
        self.csv_manager = csv_manager

    def discar_e_transferir(self, numero: str):

        print(f"Discando para {numero}...")
        subprocess.run(["adb","-s", CELULAR,"shell","am","start","-a","android.intent.action.CALL","-d",f"tel:{numero}"])

        if foi_atendido(CELULAR):
            print(f"{numero} atendeu, transferido para {NUMERO_TRANSFER}...")
            subprocess.run(["adb","-s", CELULAR,"shell","am","start","-a","android.intent.action.CALL","-d",f"tel:{NUMERO_TRANSFER}"])
            self.csv_manager.registrar_tentativa(numero,"Atendido e transferido")
        else:
            print(f"{numero} não atendeu")
            self.csv_manager.resgistrar_tentativa(numero,"Não atendido")