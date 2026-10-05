# HttpVerify

A simple HTTP availability monitor built with Python.

HttpVerify checks services at defined intervals, measures response times, logs events, and sends alerts to Discord when a service fails.

## Features

* Periodic URL monitoring
* HTTP status checks
* Latency measurement
* File logging
* Alerts via Discord Webhook
* Configuration through `.env`
* Optional service loading from an API
* Fallback to locally configured services

## Workflow

```text
Service → HTTP Request → Status
                         ├─ OK
                         └─ Failure → Log + Discord
```

## Setup

Install the dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
DISCORD_WEBHOOK_URL=your_webhook_url
API_PROJECTS_URL=
```

`API_PROJECTS_URL` is optional. If it is not set, services are loaded from `SERVICES` in the code.

> Do not commit the `.env` file to version control.

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

When configured, the API must return:

```json
[
    {
        "name": "Tasky",
        "url": "https://tasky.com"
    },
    {
        "name": "MoneyControl",
        "url": "https://moneycontrol.com"
    }
]
```

If the API fails, the monitor falls back to the local list.

## Running

```bash
python HttpVerify.py
```

Default configuration:

```python
TIMEOUT = 5
CHECK_INTERVAL = 300
```

This sets a 5-second timeout per request and runs a new check every 5 minutes.

## Discord

Alerts are sent as embeds containing the key details of the incident.

![HttpVerify alert in Discord](assets/discord-alert.png)

## Logs

Events are logged to:

```text
httpverify.log
```

The file stores technical details of failures for troubleshooting.

## Technologies

* Python
* Requests
* python-dotenv
* Discord Webhook
* Logging

## Purpose

This project was developed to practice **monitoring, automation, logging, webhook integration, and DevOps concepts**.

## Author

**Antonio**

[devantonio.com.br](https://devantonio.com.br)
