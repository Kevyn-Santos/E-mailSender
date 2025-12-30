# importação de bibliotecas
from email.message import EmailMessage
from pydantic import EmailStr
from email_validator import EmailNotValidError
import smtplib
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates as j2t
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import os
import re

# Carregamento de configurações básicas
app = FastAPI()
load_dotenv()
pages = j2t(directory='Templates')
paginaHTML = 'envio.html'

# Renderização da página web
@app.get("/", response_class=HTMLResponse)
def render(request: Request):
    return pages.TemplateResponse(paginaHTML, {"request": request})

#Construção e envio do e-mail
@app.post("/cad_sucsess")
def email_sender(user_mail: EmailStr = Form(...),
                 name_user: str = Form(..., min_length=3, max_length=100)):

    #carregamento das variaveis de ambiente
    me = os.getenv("ME")
    passwd = os.getenv("PASS")
    EmailUsuario = user_mail
    NomeUsuario = name_user
    Servidor = 'smtp.gmail.com'
    Porta = 465
    EHelo = 'localhost'

    try:
    # Validação de nome
        NomeUsuario = re.sub(r"[^A-Za-zÀ-ÖØ-öø-ÿ\s]", " ", NomeUsuario).strip()

        #Construção do e-mail com a classe EmailMessage
        msg = EmailMessage()
        msg['from'] = me
        msg['to'] = user_mail
        msg['subject'] = 'teste de envio'
        msg.set_content(f'Olá {NomeUsuario}, este é um teste de envio de mensagem')
    except EmailNotValidError as email_err:
        print(email_err)
        return email_err

    #configuração de envio
    sender = smtplib.SMTP_SSL(Servidor, port=Porta)
    try:
        sender.ehlo(EHelo)
        sender.login(me, passwd)
        sender.sendmail(msg['from'], msg['to'], msg.as_string())
        return {'E-mail enviado com sucesso para': user_mail,
                'Nome do usuario': NomeUsuario,
                'E-mail': user_mail} # Essa linha é apenas para ver o retorno
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
