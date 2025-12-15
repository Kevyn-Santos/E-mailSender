# importação de bibliotecas
from email.message import EmailMessage
import smtplib
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates as j2t
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import os

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
def email_sender(user_mail: str = Form(...), name_user: str = Form(...)):

    #carregamento das variaveis de ambiente
    me = os.getenv("ME")
    passwd = os.getenv("PASS")

    #Construção do e-mail com a classe EmailMessage
    msg = EmailMessage()
    msg['from'] = me
    msg['to'] = user_mail
    msg['subject'] = 'teste de envio'
    msg.set_content(f'Olá {name_user}, este é um teste de envio de mensagem')

    #configuração de envio
    sender = smtplib.SMTP_SSL('smtp.gmail.com', port=465)
    try:
        sender.ehlo('localhost')
        sender.login(me, passwd)
        sender.sendmail(msg['from'], msg['to'], msg.as_string())
        return
    # Capturas de erros de conexão, autenticação e informações
    except smtplib.SMTPConnectError as conn_err:
        print(conn_err)
    except smtplib.SMTPAuthenticationError as auth_err:
        print(auth_err)
    except smtplib.SMTPDataError as dt_err:
        print(dt_err)
    finally:
        #Encerra o processo de envio
        sender.quit()
