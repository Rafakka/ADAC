import subprocess
from tracker import foi_atendido
from csv_manager import CSVManager
from config import CELULAR, NUMERO_TRANSFER, CSV_PATH

csv_manager = CSVManager(CSV_PATH)

def discar_e_transferir(self, numero: str):

        print(f"Discando para {numero}...")
        subprocess.run(["adb","-s", CELULAR,"shell","am","start","-a","android.intent.action.CALL","-d",f"tel:{numero}"])

        if foi_atendido(CELULAR):
            subprocess.run(["adb","-s", CELULAR,"shell","input","keyevent","KEYCODE_CALL"])
            csv_manager.registrar_tentativa(numero,f"Atendido e transferido para{NUMERO_TRANSFER}")
        else:
            csv_manager.resgistrar_tentativa(numero,"Não atendido")