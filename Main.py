# importação de bibliotecas
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template
from requests import sessions

from pydantic import EmailStr,BaseModel
import smtplib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import api_key

from dotenv import load_dotenv
import os
import re
from pathlib import Path

# Carregamento de configurações básicas
app = FastAPI()
app.add_middleware( # Permissões CORS
    CORSMiddleware,
    allow_origins=[
        "null",                     # ← necessário quando abre via file://
        "http://localhost",
        "http://127.0.0.1",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"                         # opcional: permite literalmente tudo (use só em dev)
    ],
    allow_credentials=True,         # se precisar de cookies ou auth no futuro
    allow_methods=["*"],            # GET, POST, OPTIONS, etc.
    allow_headers=["*"],
)

load_dotenv()
me = os.getenv("SENDER")
passwd = os.getenv("PASS")
Servidor = os.getenv("SMTP_SERVER",'smtp.gmail.com')
Porta = int(os.getenv("PORT_SMTP",465))
EHelo = os.getenv("EHELO",'localhost')
Caminho_mensagem: str = os.getenv("MSG_PATH") # type: ignore
Assunto:str = os.getenv("SUBJECT") #type: ignore

if not all([Caminho_mensagem, me, passwd]): # validação de váriaveis de ambiente preenchidas
        raise RuntimeError('Variaveis de ambiente SENDER, PASS ou MSG_PATH não definidas')
 
# Criação da classe de recebimento de informações
class info_reciver(BaseModel):
    user_mail: EmailStr
    name_user: str

    def formatar_nome(self):
        name_user = re.sub(r"[^A-Za-zÀ-ÖØ-öø-ÿ\s]", " ", self.name_user).strip()
        return " ".join(name_user.split())  # remove múltiplos espaços


#TODO Rate Limiter
#TODO Autenticação


#Construção e envio do e-mail
@app.post("/sendMail")
def email_sender(user: info_reciver):
    EmailUsuario = user.user_mail
    NomeUsuario = user.formatar_nome()
    
    # Valida se arquivo de mensagens foi encontrado
    caminho_arquivo = Path(Caminho_mensagem)
    if not caminho_arquivo.is_file():
        raise HTTPException(status_code=500, detail=f'Diretório não encontrado: {caminho_arquivo}')

    try:
        #Construção do e-mail com a classe EmailMessage
        with open(caminho_arquivo) as fp:
            msgTemp = fp.read()
            msgdef =  Template(msgTemp).safe_substitute(usuario= NomeUsuario, email= EmailUsuario, ) # Sanitização de input de nome

        msg = MIMEMultipart()
        msg['from'] = me # type: ignore
        msg['to'] = EmailUsuario
        msg['subject'] = Assunto
        msg.attach(MIMEText(msgdef, 'plain', 'utf-8'))

        #configuração de envio
        with smtplib.SMTP_SSL(Servidor, port=Porta) as sender:
            sender.ehlo(EHelo)
            sender.login(me, passwd) # type: ignore
            sender.send_message(msg) # -> Automaticamente lê tudo do objeto msg


    # Capturas de erros de conexão, autenticação e informações
    except smtplib.SMTPConnectError:
        raise HTTPException(500, detail='Não foi possivel conectar com o servidor SMTP')
    except smtplib.SMTPAuthenticationError:
        raise HTTPException(500, detail='Falha de autenticação SMTP: Email ou Senha incorretos')
    # except Exception as e:
    #   raise HTTPException(500, detail=f"Erro: {str(e)}") # Registro de algum erro geral