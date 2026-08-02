from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP_SSL, SMTPAuthenticationError, SMTPConnectError

from fastapi import HTTPException

from src.core.settings import settings


def buildMail(to: str, name: str, path) -> MIMEMultipart:
    with open(path) as fp:
        body = fp.read().format(usuario=name, email=to)

    msg = MIMEMultipart()
    msg["from"] = settings.SENDER  # type: ignore
    msg["to"] = to
    msg["subject"] = settings.SUBJECT
    msg.attach(MIMEText(body, "plain", "utf-8"))
    return msg


def sendMail(to: str, name: str):
    filepath = settings.path_validator()

    try:
        msg = buildMail(to, name, filepath)
        with SMTP_SSL(host=settings.SMTP_SERVER, port=settings.PORT_SMTP) as sender:
            sender.ehlo(settings.EHELO)
            sender.login(settings.SENDER, settings.PASS)  # type: ignore
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
