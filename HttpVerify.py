import requests
import time
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TIMEOUT = 5
CHECK_INTERVAL = 300

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
API_PROJECTS_URL = os.getenv("API_PROJECTS_URL", "")

# Serviços monitorados localmente
SERVICES = [
    {
        "name": "Meu Portfólio",
        "url": "https://devantonio.com.br"
    },
    {
        "name": "Google",
        "url": "https://google.com"
    },
    {
        "name": "Teste Fora do Ar",
        "url": "https://issonaoexiste123456.com"
    }
]

# Configuração dos logs
logging.basicConfig(
    filename="httpverify.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def send_discord_alert(
    service_name,
    status,
    url,
    message,
    elapsed=None
):
    # Evita enviar requisições sem webhook configurado
    if not DISCORD_WEBHOOK_URL:
        logging.warning(
            "DISCORD_WEBHOOK_URL não configurada."
        )
        return

    # Define a cor do alerta de acordo com o status
    color = 15158332 if status == "OFFLINE" else 16753920

    fields = [
        {
            "name": "Serviço",
            "value": service_name,
            "inline": True
        },
        {
            "name": "Status",
            "value": status,
            "inline": True
        },
        {
            "name": "Horário",
            "value": datetime.now().strftime(
                "%d/%m/%Y %H:%M:%S"
            ),
            "inline": True
        },
        {
            "name": "URL",
            "value": url,
            "inline": False
        }
    ]

    # Mostra a latência quando a requisição recebeu resposta
    if elapsed is not None:
        fields.append({
            "name": "Tempo de resposta",
            "value": f"{elapsed} ms",
            "inline": True
        })

    fields.append({
        "name": "Detalhes",
        "value": message,
        "inline": False
    })

    payload = {
        "username": "HttpVerify",
        "embeds": [
            {
                "title": "HttpVerify — Alerta de Monitoramento",
                "color": color,
                "fields": fields,
                "footer": {
                    "text": "HttpVerify • Monitoramento de serviços"
                },
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        ]
    }

    try:
        response = requests.post(
            DISCORD_WEBHOOK_URL,
            json=payload,
            timeout=TIMEOUT
        )

        response.raise_for_status()

        logging.info(
            f"Alerta enviado ao Discord: {service_name}"
        )

    except requests.exceptions.RequestException as e:
        logging.error(
            f"Falha ao enviar alerta para o Discord: {e}"
        )


def get_services():
    """Busca os serviços monitorados pela API configurada."""

    if not API_PROJECTS_URL:
        logging.warning(
            "API_PROJECTS_URL não configurada."
        )
        return []

    try:
        response = requests.get(
            API_PROJECTS_URL,
            timeout=TIMEOUT
        )

        response.raise_for_status()

        services = response.json()

        if not isinstance(services, list):
            logging.error(
                "A API retornou um formato inválido."
            )
            return []

        logging.info(
            f"{len(services)} serviços carregados pela API."
        )

        return services

    except requests.exceptions.RequestException as e:
        logging.error(
            f"Falha ao buscar serviços pela API: {e}"
        )
        return []

    except ValueError as e:
        logging.error(
            f"Resposta JSON inválida da API: {e}"
        )
        return []


def check_service(service):
    try:
        # Inicia a contagem para medir a latência
        start = time.time()

        response = requests.get(
            service["url"],
            timeout=TIMEOUT
        )

        elapsed = round(
            (time.time() - start) * 1000,
            2
        )

        # Status 200 indica uma resposta normal
        if response.status_code == 200:
            msg = (
                f"{service['name']} ONLINE - "
                f"{elapsed}ms"
            )

            logging.info(msg)
            print(msg)

            return True

        # Outros códigos HTTP são tratados como alerta
        msg = (
            f"{service['name']} respondeu "
            f"HTTP {response.status_code}"
        )

        logging.warning(msg)
        print(msg)

        send_discord_alert(
            service_name=service["name"],
            status=f"HTTP {response.status_code}",
            url=service["url"],
            message=(
                "O serviço respondeu, mas retornou "
                "um código HTTP diferente de 200."
            ),
            elapsed=elapsed
        )

        return False

    except requests.exceptions.RequestException as e:
        # Guarda o erro técnico completo no arquivo de log
        logging.error(
            f"{service['name']} FORA DO AR - {e}"
        )

        print(
            f"{service['name']} FORA DO AR"
        )

        # Envia uma mensagem resumida para o Discord
        send_discord_alert(
            service_name=service["name"],
            status="OFFLINE",
            url=service["url"],
            message=(
                "O serviço não respondeu corretamente "
                "dentro do tempo limite ou não pôde ser acessado."
            )
        )

        return False


def run_checks():
    # Usa a API quando configurada; caso contrário, usa a lista local
    if API_PROJECTS_URL:
        services = get_services()

        # Se a API falhar, mantém a lista local como fallback
        if not services:
            logging.warning(
                "API indisponível. Usando serviços locais."
            )
            services = SERVICES
    else:
        services = SERVICES

    print()
    print("HttpVerify - Verificação de Serviços")
    print(
        f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    )

    total = len(services)
    online = 0
    offline = 0

    for service in services:
        if check_service(service):
            online += 1
        else:
            offline += 1

    # Exibe o resumo da verificação
    print()
    print(f"Serviços monitorados: {total}")
    print(f"Online: {online}")
    print(f"Com problemas: {offline}")
    print("Log: httpverify.log")
    print()


def main():
    print("HttpVerify iniciado.")
    print(
        f"Intervalo: {CHECK_INTERVAL // 60} minutos"
    )
    print(
        f"Timeout: {TIMEOUT} segundos"
    )
    print("Pressione CTRL+C para parar.")
    print()

    while True:
        try:
            run_checks()

            # Aguarda até a próxima verificação
            print(
                f"Próxima verificação em "
                f"{CHECK_INTERVAL // 60} minutos."
            )

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            # Permite encerrar o monitoramento com CTRL+C
            print()
            print("HttpVerify encerrado.")

            logging.info(
                "HttpVerify encerrado pelo usuário."
            )

            break


if __name__ == "__main__":
    main()