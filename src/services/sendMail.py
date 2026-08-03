from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP_SSL, SMTPAuthenticationError, SMTPConnectError

from fastapi import HTTPException

from src.core.mail_config import ResolvedMailConfig


def buildMail(to: str, name: str, config: ResolvedMailConfig) -> MIMEMultipart:
    body = config.template.format(usuario=name, email=to)

    msg = MIMEMultipart()
    msg["from"] = config.sender
    msg["to"] = to
    msg["subject"] = config.subject
    msg.attach(MIMEText(body, "plain", "utf-8"))
    return msg


def sendMail(to: str, name: str, config: ResolvedMailConfig):
    try:
        msg = buildMail(to, name, config)
        with SMTP_SSL(host=config.smtp_server, port=config.port_smtp) as sender:
            sender.ehlo(config.ehelo)
            sender.login(config.sender, config.password)
            sender.send_message(msg)  # -> Automaticamente lê tudo do objeto msg

    except SMTPConnectError as e:
        raise HTTPException(
            500, detail="Não foi possivel conectar com o servidor SMTP"
        ) from e
    except SMTPAuthenticationError as e:
        raise HTTPException(
            500, detail="Falha de autenticação SMTP: Email ou Senha incorretos"
        ) from e
    except KeyError as e:
        raise HTTPException(500, detail=f"Template com variável inválida: {e}") from e
