# importação de bibliotecas
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pydantic import EmailStr,BaseModel
import smtplib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import api_key

from dotenv import load_dotenv
import os
import re
from pathlib import Path

# Carregamento das variaveis de ambiente
load_dotenv()
me = os.getenv("SENDER")
passwd = os.getenv("PASS")
Servidor = os.getenv("SMTP_SERVER",'smtp.gmail.com')
Porta = int(os.getenv("PORT_SMTP",465))
EHelo = os.getenv("EHELO",'localhost')
Caminho_mensagem: str = os.getenv("MSG_PATH") # type: ignore
Assunto:str = os.getenv("SUBJECT") #type: ignore
hosts = os.getenv('HOSTS', "http://localhost")

# Verifica os IP's passados em 'hosts', remove seus espaços e caracteres desnecessários, e os passa em URL's_permitidas.
if hosts:
    URLs_permitidas = []
    for part in hosts.split(','):
        clean = part.strip()
        if clean and clean.lower() != 'null' and clean != '*':
            if clean.endswith('/'):
                clean = clean.rstrip('/')
            URLs_permitidas.append(clean)
    
    Commons = { # URL's comuns que podem ser utilizadas em DEV
        "http://localhost",
        "http://localhost:5500",
        "http://127.0.0.1",
        "http://127.0.0.1:5500",
        "http://127.0.0.1:8000"
    }
    URLs_permitidas = list(set(URLs_permitidas + list(Commons)))
else:
    URLs_permitidas=['*'] # Caso hosts não esteja preenchido, define URL's permitidas para passar todos os valores

# Carregamento de configurações básicas
app = FastAPI()
app.add_middleware( # Permissões CORS
    CORSMiddleware,
    allow_origins=URLs_permitidas, # Hosts tratados na condicional anterior
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not all([Caminho_mensagem, me, passwd]): # validação de váriaveis de ambiente preenchidas
        raise RuntimeError('Variaveis de ambiente SENDER, PASS ou MSG_PATH não definidas')
 
# Criação da classe de recebimento de informações
class base_User(BaseModel):
    user_mail: EmailStr
    name_user: str

    def formatar_nome(self):
        name_user = re.sub(r"[^A-Za-zÀ-ÖØ-öø-ÿ\s]", " ", self.name_user).strip()
        return " ".join(name_user.split())  # remove múltiplos espaços


#TODO Rate Limiter
#TODO Autenticação
#TODO Logging

#Construção e envio do e-mail
@app.post("/sendMail")
def email_sender(user: base_User):
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
            msgdef = msgTemp.format(usuario=NomeUsuario, email=EmailUsuario) # Sanitização de input de nome

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