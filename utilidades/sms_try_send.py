#!/usr/bin/env python3
"""
sms_try_send.py

Tentativa em cascata para abrir / preparar SMS no aparelho via ADB:
  1) Intent SENDTO (abrir app de SMS com número e corpo já preenchidos) - preferido
  2) Se falhar, procurar apps de SMS comuns e abrir um deles
  3) Se um app abrir, tentar injetar número/mensagem via `input text` e sugerir enviar manualmente

Uso:
  python sms_try_send.py --number "+5511..." --message "Texto de teste" [--adb "/path/to/adb"] [--serial "DEVICE_SERIAL"]

Observações:
 - Não garante envio automático (depende da ROM / permissões).
 - Para envio automático confiável é preciso app com SEND_SMS ou root.
"""

import subprocess
import argparse
import logging
import shlex
import time
import sys

# Configuração
COMMON_SMS_PACKAGES = [
    "com.google.android.apps.messaging",
    "com.android.messaging",
    "com.android.mms",
    "com.samsung.android.messaging",
    "com.miui.messaging",
    "com.tencent.mtt",  # placeholder
]


# Logger simples
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def run_adb(cmd_args, adb_path="adb", device_serial=None, timeout=15):
    """Executa adb (lista de argumentos) e retorna (returncode, stdout, stderr)."""
    base = [adb_path]
    if device_serial:
        base += ["-s", device_serial]
    base += cmd_args
    try:
        p = subprocess.run(base, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except Exception as e:
        return 99, "", str(e)

def try_intent_sendto(number, message, adb_path="adb", device_serial=None):
    """Tenta abrir app de SMS via Intent SENDTO (o método mais usado)."""
    logging.info("Tentando Intent SENDTO (abrir app de SMS com número e corpo preenchidos)...")
    # proteger mensagem com shlex.quote na hora de montar, mas subprocess list evita shell expansion
    cmd = [
        "shell", "am", "start",
        "-a", "android.intent.action.SENDTO",
        "-d", f"sms:{number}",
        "--es", "sms_body", message,
        "--ez", "exit_on_sent", "true"
    ]
    rc, out, err = run_adb(cmd, adb_path, device_serial)
    logging.debug("adb out: %s", out)
    logging.debug("adb err: %s", err)
    if rc == 0:
        logging.info("Intent SENDTO executado (verifique o celular).")
        return True
    else:
        logging.warning("Intent SENDTO falhou. rc=%s, stderr=%s", rc, err)
        return False

def package_exists(pkg, adb_path="adb", device_serial=None):
    rc, out, err = run_adb(["shell", "pm", "list", "packages", pkg], adb_path, device_serial)
    return (rc == 0 and pkg in out)

def try_open_common_sms_app(adb_path="adb", device_serial=None):
    """Tenta localizar + abrir um app de SMS conhecido."""
    logging.info("Procurando apps de SMS instalados...")
    for pkg in COMMON_SMS_PACKAGES:
        if package_exists(pkg, adb_path, device_serial):
            logging.info("Encontrado pacote SMS: %s. Tentando abrir.", pkg)
            # Tentativa de abrir via monkey (lança launcher activity do pacote)
            rc, out, err = run_adb(["shell", "monkey", "-p", pkg, "-c", "android.intent.category.LAUNCHER", "1"], adb_path, device_serial)
            if rc == 0:
                logging.info("App %s iniciado (usando monkey). Aguarde 1s e verifique o celular.", pkg)
                time.sleep(1.2)
                return pkg
            else:
                logging.warning("Falha ao iniciar %s via monkey. rc=%s err=%s", pkg, rc, err)
    logging.info("Nenhum app SMS comum foi iniciado.")
    return None

def inject_text(adb_path, device_serial, text):
    """Injeta texto via `adb shell input text`. Escapa espaços com %s ou usando shlex."""
    # `input text` aceita espaços se escapados; vamos usar replace para espaços -> %s (works reasonably)
    safe = text.replace(" ", "%s")
    rc, out, err = run_adb(["shell", "input", "text", safe], adb_path, device_serial)
    return rc == 0

def try_inject_number_and_message(number, message, adb_path="adb", device_serial=None):
    """
    Método frágil: assume que app de SMS está aberto e foco está num campo editável.
    Passos:
      - injeta número (se o app oferece campo para isso)
      - injeta mensagem
      - tenta tecla ENTER (66) — pode ou não enviar dependendo do app
    """
    logging.info("Tentando injetar número e mensagem (método frágil).")
    # injetar número
    ok_num = inject_text(adb_path, device_serial, number)
    time.sleep(0.4)
    # tentar confirmar (tecla TAB/ENTER pode variar)
    run_adb(["shell", "input", "keyevent", "61"], adb_path, device_serial)  # KEYCODE_TAB (61)
    time.sleep(0.3)
    # injetar mensagem
    ok_msg = inject_text(adb_path, device_serial, message)
    time.sleep(0.3)
    # tentar ENTER
    run_adb(["shell", "input", "keyevent", "66"], adb_path, device_serial)  # KEYCODE_ENTER
    return ok_num or ok_msg

def test_prepare_sms(number, message, adb_path="adb", device_serial=None):
    """Fluxo: try Intent -> try open package -> try injection -> pedir confirmação."""
    logging.info("=== Iniciando tentativa de preparar SMS ===")
    if try_intent_sendto(number, message, adb_path, device_serial):
        logging.info("Intent funcionou — verifique o celular e confirme envio manual.")
        return True

    logging.info("Tentativa com Intent falhou. Tentando abrir app SMS instalado...")
    pkg = try_open_common_sms_app(adb_path, device_serial)
    if not pkg:
        logging.warning("Não foi possível abrir app de SMS conhecido.")
        return False

    logging.info("App potencialmente aberto. Tentando injetar número e mensagem...")
    injected = try_inject_number_and_message(number, message, adb_path, device_serial)
    if injected:
        logging.info("Texto injetado (possivelmente). Verifique o celular e finalize o envio manualmente.")
        return True
    else:
        logging.warning("Falha ao injetar texto no app. Será necessário enviar manualmente.")
        return False

def adb_check(adb_path="adb"):
    rc,out,err = run_adb(["version"], adb_path)
    if rc == 0:
        logging.info("ADB encontrado: %s", out.splitlines()[0] if out else "versão desconhecida")
        return True
    else:
        logging.error("ADB não encontrado ou falha: %s", err)
        return False

def parse_args():
    p = argparse.ArgumentParser(description="Tentativa de preparar SMS via ADB (Intent -> abrir app -> inject)")
    p.add_argument("--number", "-n", required=True, help="Número destino (ex: +5511999999999)")
    p.add_argument("--message", "-m", required=True, help="Texto da mensagem")
    p.add_argument("--adb", default="adb", help="Caminho para adb (padrão: adb no PATH)")
    p.add_argument("--serial", "-s", default=None, help="Serial do dispositivo (opcional)")
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    ADB = args.adb
    SERIAL = args.serial

    if not adb_check(ADB):
        logging.error("Abortando: adb não disponível.")
        sys.exit(1)

    ok = test_prepare_sms(args.number, args.message, adb_path=ADB, device_serial=SERIAL)
    if ok:
        logging.info("Fim do fluxo: verifique o aparelho e confirme o envio manual.")
    else:
        logging.error("Todas tentativas falharam. Considere app auxiliar (requere permissão SEND_SMS) ou automação UI.")
