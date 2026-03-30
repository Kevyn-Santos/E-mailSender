from fastapi import HTTPException, APIRouter
from smtplib import (SMTPConnectError, SMTPAuthenticationError, SMTP_SSL)
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from core.settings import settings
from models.emailModules import baseUser


routers = APIRouter(prefix='/sendMail', tags=['SendEmail'])

@routers.post('/sendMail')
def email_sender(User: baseUser):
    userMail = User.userMail
    nameUser = User.userName
    filepath = settings.path_validator()

    try:
        with open(filepath) as fp:
            msgTemp = fp.read()
            msgdef = msgTemp.format(usuario=nameUser, email=userMail)
        
        msg=MIMEMultipart()
        msg['from'] = settings.SENDER #type: ignore
        msg['to'] = userMail
        msg['subject'] = settings.SUBJECT
        msg.attach(MIMEText(msgdef, 'plain', 'utf-8'))

        with SMTP_SSL(host=settings.SMTP_SERVER, port=settings.PORT_SMTP) as sender:
            sender.ehlo(settings.EHELO)
            sender.login(settings.SENDER, settings.PASS) # type: ignore
            sender.send_message(msg) # -> Automaticamente lê tudo do objeto msg

    except SMTPConnectError:
        raise HTTPException(500, detail='Não foi possivel conectar com o servidor SMTP')
    except SMTPAuthenticationError:
        raise HTTPException(500, detail='Falha de autenticação SMTP: Email ou Senha incorretos')