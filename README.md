# HttpVerify

Simple HTTP availability monitor developed in Python.

HttpVerify checks services at defined intervals, measures response time, logs events, and sends alerts to Discord when a service fails.

## Features

* Periodic URL monitoring
* HTTP status verification
* Latency measurement
* File logging
* Discord Webhook alerts
* `.env` configuration
* Optional service loading via API
* Fallback to locally configured services

## Flow

```text
Service → HTTP Request → Status
                      ├─ OK
                      └─ Failure → Log + Discord
```

## Configuration

Install the dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the root:

```env
DISCORD_WEBHOOK_URL=your_webhook_url
API_PROJECTS_URL=
```

`API_PROJECTS_URL` is optional. Without it, services are loaded from `SERVICES` in the code.

### Services

```python
SERVICES = [
    {
        "name": "My Portfolio",
        "url": "https://devantonio.com.br"
    },
    {
        "name": "Google",
        "url": "https://google.com"
    }
]
```

### Services API

When configured, the API should return:

```json
[
    {
        "name": "Tasky",
        "url": "https://tasky.com"
    }
]
```

If the API fails, the monitor uses the local list as a fallback.

## Execution

```bash
python HttpVerify.py
```

Default configuration:

```python
TIMEOUT = 5
CHECK_INTERVAL = 300
```

This represents a 5-second timeout per request and a new check every 5 minutes.

## Discord

Alerts are sent as Embeds containing the main details of the incident.

![HttpVerify Alert on Discord](assets/discord-alert.png)

## Logs

Events are recorded in:

```text
httpverify.log
```

The file keeps the technical details of failures for diagnosis.

## Technologies

* Python
* Requests
* python-dotenv
* Discord Webhook
* Logging
