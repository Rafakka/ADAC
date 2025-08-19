import subprocess
import time

def foi_atendido(celular):
    tentativas = 0
    while tentativas < 3:
        result = subprocess.run(["adb","-s", celular,"shell","dumpsys","telecom"],
                                capture_output=True, text=True
                                )
        if"CallState:OFFHOOK" in results.stdout:
            return True
        time.sleep(1)
        tentativas += 1
        return False