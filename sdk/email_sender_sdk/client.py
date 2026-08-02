import os
from pathlib import Path

import httpx


class EmailSenderClient:
    """Cliente para a API multi-tenant de envio de e-mails.

    Guarda a configuração de envio (remetente, senha, template, etc.) do dev
    localmente e monta o payload do POST /sendMail automaticamente.
    """

    def __init__(
        self,
        base_url: str,
        sender: str | None = None,
        password: str | None = None,
        smtp_server: str | None = None,
        port_smtp: int | None = None,
        ehelo: str | None = None,
        subject: str | None = None,
        template: str | None = None,
        template_path: str | Path | None = None,
        timeout: float = 10.0,
    ):
        if template_path is not None:
            template = Path(template_path).read_text(encoding="utf-8")

        self.base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._config = {
            "sender": sender,
            "password": password,
            "smtp_server": smtp_server,
            "port_smtp": port_smtp,
            "ehelo": ehelo,
            "subject": subject,
            "template": template,
        }

    @classmethod
    def from_env(cls, base_url: str, prefix: str = "EMAIL_SENDER_") -> "EmailSenderClient":
        """Constrói o cliente lendo a configuração das variáveis de ambiente do
        PROJETO DO DEV (não confundir com o .env do servidor da API)."""
        port_smtp_env = os.getenv(f"{prefix}PORT_SMTP")
        return cls(
            base_url=base_url,
            sender=os.getenv(f"{prefix}SENDER"),
            password=os.getenv(f"{prefix}PASSWORD"),
            smtp_server=os.getenv(f"{prefix}SMTP_SERVER"),
            port_smtp=int(port_smtp_env) if port_smtp_env else None,
            ehelo=os.getenv(f"{prefix}EHELO"),
            subject=os.getenv(f"{prefix}SUBJECT"),
            template=os.getenv(f"{prefix}TEMPLATE"),
            template_path=os.getenv(f"{prefix}TEMPLATE_PATH"),
        )

    def send(self, user_mail: str, user_name: str) -> httpx.Response:
        config = {chave: valor for chave, valor in self._config.items() if valor is not None}
        payload = {"userMail": user_mail, "userName": user_name}
        if config:
            payload["config"] = config

        response = httpx.post(f"{self.base_url}/sendMail", json=payload, timeout=self._timeout)
        response.raise_for_status()
        return response
