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

# Locally monitored services
SERVICES = [
    {
        "name": "My Portfolio",
        "url": "https://devantonio.com.br"
    },
    {
        "name": "Google",
        "url": "https://google.com"
    },
    {
        "name": "Offline Test",
        "url": "https://issonaoexiste123456.com"
    }
]

# Logging configuration
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
    # Skip requests when no webhook is configured
    if not DISCORD_WEBHOOK_URL:
        logging.warning(
            "DISCORD_WEBHOOK_URL is not configured."
        )
        return

    # Set the alert color based on the status
    color = 15158332 if status == "OFFLINE" else 16753920

    fields = [
        {
            "name": "Service",
            "value": service_name,
            "inline": True
        },
        {
            "name": "Status",
            "value": status,
            "inline": True
        },
        {
            "name": "Time",
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

    # Show latency when the request received a response
    if elapsed is not None:
        fields.append({
            "name": "Response time",
            "value": f"{elapsed} ms",
            "inline": True
        })

    fields.append({
        "name": "Details",
        "value": message,
        "inline": False
    })

    payload = {
        "username": "HttpVerify",
        "embeds": [
            {
                "title": "HttpVerify — Monitoring Alert",
                "color": color,
                "fields": fields,
                "footer": {
                    "text": "HttpVerify • Service monitoring"
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
            f"Alert sent to Discord: {service_name}"
        )

    except requests.exceptions.RequestException as e:
        logging.error(
            f"Failed to send alert to Discord: {e}"
        )


def get_services():
    """Fetch monitored services from the configured API."""

    if not API_PROJECTS_URL:
        logging.warning(
            "API_PROJECTS_URL is not configured."
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
                "The API returned an invalid format."
            )
            return []

        logging.info(
            f"{len(services)} services loaded from the API."
        )

        return services

    except requests.exceptions.RequestException as e:
        logging.error(
            f"Failed to fetch services from the API: {e}"
        )
        return []

    except ValueError as e:
        logging.error(
            f"Invalid JSON response from the API: {e}"
        )
        return []


def check_service(service):
    try:
        # Start the timer to measure latency
        start = time.time()

        response = requests.get(
            service["url"],
            timeout=TIMEOUT
        )

        elapsed = round(
            (time.time() - start) * 1000,
            2
        )

        # Status 200 indicates a normal response
        if response.status_code == 200:
            msg = (
                f"{service['name']} ONLINE - "
                f"{elapsed}ms"
            )

            logging.info(msg)
            print(msg)

            return True

        # Treat other HTTP codes as alerts
        msg = (
            f"{service['name']} returned "
            f"HTTP {response.status_code}"
        )

        logging.warning(msg)
        print(msg)

        send_discord_alert(
            service_name=service["name"],
            status=f"HTTP {response.status_code}",
            url=service["url"],
            message=(
                "The service responded but returned "
                "an HTTP status code other than 200."
            ),
            elapsed=elapsed
        )

        return False

    except requests.exceptions.RequestException as e:
        # Save the full technical error in the log file
        logging.error(
            f"{service['name']} OFFLINE - {e}"
        )

        print(
            f"{service['name']} OFFLINE"
        )

        # Send a brief message to Discord
        send_discord_alert(
            service_name=service["name"],
            status="OFFLINE",
            url=service["url"],
            message=(
                "The service did not respond correctly "
                "within the timeout period or could not be reached."
            )
        )

        return False


def run_checks():
    # Use the API when configured; otherwise, use the local list
    if API_PROJECTS_URL:
        services = get_services()

        # Fall back to the local list if the API fails
        if not services:
            logging.warning(
                "API unavailable. Using local services."
            )
            services = SERVICES
    else:
        services = SERVICES

    print()
    print("HttpVerify - Service Check")
    print(
        f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    )

    total = len(services)
    online = 0
    offline = 0

    for service in services:
        if check_service(service):
            online += 1
        else:
            offline += 1

    # Display the check summary
    print()
    print(f"Monitored services: {total}")
    print(f"Online: {online}")
    print(f"With issues: {offline}")
    print("Log: httpverify.log")
    print()


def main():
    print("HttpVerify started.")
    print(
        f"Interval: {CHECK_INTERVAL // 60} minutes"
    )
    print(
        f"Timeout: {TIMEOUT} seconds"
    )
    print("Press CTRL+C to stop.")
    print()

    while True:
        try:
            run_checks()

            # Wait until the next check
            print(
                f"Next check in "
                f"{CHECK_INTERVAL // 60} minutes."
            )

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            # Allow monitoring to stop with CTRL+C
            print()
            print("HttpVerify stopped.")

            logging.info(
                "HttpVerify stopped by the user."
            )

            break


if __name__ == "__main__":
    main()
