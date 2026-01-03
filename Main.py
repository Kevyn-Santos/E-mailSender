# importação de bibliotecas
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import abspath

from pydantic import EmailStr
from email_validator import EmailNotValidError
import smtplib
from fastapi import FastAPI, Request, Form

from dotenv import load_dotenv
import os
import re
# Carregamento de configurações básicas
app = FastAPI()
load_dotenv()

#Construção e envio do e-mail
@app.post("/cad_sucsess")
def email_sender(user_mail: EmailStr = Form(...),
                 name_user: str = Form(..., min_length=3, max_length=100)):

    #carregamento das variaveis de ambiente
    me = os.getenv("SENDER")
    passwd = os.getenv("PASS")
    Servidor = os.getenv("SMTP_SERVER",'smtp.gmail.com')
    Porta = int(os.getenv("PORT_SMTP",465))
    EHelo = os.getenv("EHELO",'localhost')
    Caminho_mensagem = abspath(os.getenv("MSG_PATH", "/Assets"))
    EmailUsuario = user_mail
    NomeUsuario = name_user

    try:
    # Validação de nome
        NomeUsuario = re.sub(r"[^A-Za-zÀ-ÖØ-öø-ÿ\s]", " ", NomeUsuario).strip()
        if not Caminho_mensagem:
            raise FileNotFoundError(f'diretorio de mensagens {Caminho_mensagem} não enccontrado')


        #Construção do e-mail com a classe EmailMessage
        with open(f'{Caminho_mensagem}.txt') as fp:
            msgTemp = fp.read()

        # msg = EmailMessage()
        msgdef = msgTemp.format(usuario= NomeUsuario, email= user_mail)
        msg = MIMEMultipart()
        msg['from'] = me
        msg['to'] = user_mail
        msg['subject'] = f'teste de envio'
        msg.attach(MIMEText(msgdef, 'plain', 'utf-8'))

    except EmailNotValidError as email_err:
        return email_err

    #configuração de envio
    sender = smtplib.SMTP_SSL(Servidor, port=Porta)
    try:
        sender.ehlo(EHelo)
        sender.login(me, passwd)
        sender.sendmail(msg['from'], msg['to'], msg.as_string())
        return
    # Capturas de erros de conexão, autenticação e informações
    except smtplib.SMTPConnectError as conn_err:
        raise conn_err
        return conn_err
        sender.quit()
    except smtplib.SMTPAuthenticationError as auth_err:
        raise auth_err
        return auth_err
        sender.quit()
    except smtplib.SMTPDataError as dt_err:
        raise dt_err
        return dt_err
        sender.quit()
    finally:
        #Encerra o processo de envio
        sender.quit()