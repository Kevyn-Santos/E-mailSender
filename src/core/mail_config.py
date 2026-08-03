from dataclasses import dataclass

from fastapi import HTTPException

from src.core.settings import settings
from src.models.emailModules import MailConfig


@dataclass(frozen=True)
class ResolvedMailConfig:
    """Configuração final de envio, já mesclada request > ENV > default."""

    sender: str
    password: str
    smtp_server: str
    port_smtp: int
    ehelo: str
    subject: str
    template: str


def _default_template() -> str:
    """Lê o template padrão empacotado com a API quando nenhum for informado."""
    filepath = settings.path_validator()
    with open(filepath, encoding="utf-8") as arquivo_template:
        return arquivo_template.read()


def resolve_mail_config(request_config: MailConfig | None) -> ResolvedMailConfig:
    """Mescla configuração campo a campo: valor do request > ENV (settings) > default."""
    config = request_config or MailConfig()

    sender = config.sender or settings.SENDER
    password = config.password or settings.PASS

    if sender is None or password is None:
        raise HTTPException(
            status_code=422,
            detail="Configuração incompleta: 'sender' e 'password' devem ser informados "
            "no request ou via variáveis de ambiente do servidor.",
        )

    template = config.template if config.template is not None else _default_template()

    return ResolvedMailConfig(
        sender=sender,
        password=password,
        smtp_server=config.smtp_server or settings.SMTP_SERVER,
        port_smtp=config.port_smtp if config.port_smtp is not None else settings.PORT_SMTP,
        ehelo=config.ehelo or settings.EHELO,
        subject=config.subject if config.subject is not None else settings.SUBJECT,
        template=template,
    )
