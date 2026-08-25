# HttpVerify

Script em Python que monitora se sites/serviços estão no ar e envia alertas no Discord quando algo cai.

## Funcionalidades

- Checagem periódica de URLs
- Log em arquivo (`httpverify.log`)
- Alerta automático no Discord via webhook (só quando dá erro)

## Configuração

Crie um arquivo `.env` na raiz do projeto:

```
DISCORD_WEBHOOK_URL=sua_url_do_webhook_aqui
```

Edite a lista de sites no `HttpVerify.py`:

```python
SERVICES = [
    {"name": "Meu Site", "url": "https://meusite.com.br"},
]
```

## Uso

```bash
python HttpVerify.py
```

## Tecnologias

- Python
- requests
- python-dotenv

## Autor

[Antonio](https://devantonio.com.br)
