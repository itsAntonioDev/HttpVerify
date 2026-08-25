import requests
import time
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    filename="httpverify.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")

SERVICES = [
    {"name": "Meu Portfólio", "url": "https://devantonio.com.br"},
    {"name": "Google", "url": "https://google.com"},
]

TIMEOUT = 5
CHECK_INTERVAL = 300


def send_discord_alert(message):
    if not DISCORD_WEBHOOK_URL:
        return

    payload = {"content": message}
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=TIMEOUT)
    except requests.exceptions.RequestException as e:
        logging.error(f"Falha ao enviar alerta pro Discord: {e}")


def check_service(service):
    try:
        start = time.time()
        response = requests.get(service["url"], timeout=TIMEOUT)
        elapsed = round((time.time() - start) * 1000, 2)

        if response.status_code == 200:
            msg = f"{service['name']} OK - {elapsed}ms"
            logging.info(msg)
        else:
            msg = f"{service['name']} respondeu status {response.status_code}"
            logging.warning(msg)
            send_discord_alert(f"[ALERTA] {msg}")

        print(msg)
        return True

    except requests.exceptions.RequestException as e:
        msg = f"{service['name']} FORA DO AR - {e}"
        logging.error(msg)
        print(msg)
        send_discord_alert(f"[CRITICO] {msg}")
        return False


def run_checks():
    print(f"\n--- HttpVerify {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} ---")
    for service in SERVICES:
        check_service(service)
    print(f"--- Fim do check (log salvo em httpverify.log) ---\n")


def main():
    print(f"HttpVerify iniciado. Checando a cada {CHECK_INTERVAL} segundos.")
    print("Pressione CTRL+C para parar.\n")
    while True:
        run_checks()
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()