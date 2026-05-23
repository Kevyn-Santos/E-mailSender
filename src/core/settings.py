from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import (EmailStr, AnyUrl, BeforeValidator, computed_field)
from fastapi import HTTPException
from typing import Annotated, Any
from pathlib import Path


# limpa os IP's que virão de CORS
def cors_config(Urls: Any) -> list[str]: #type: ignore
    if isinstance(Urls, list):
        return[str(u).strip() for u in Urls] # Se for lista, retira os espaços
    
    if isinstance(Urls, str):
        clean = Urls.strip().strip('[]')
        return[u.strip() for u in clean.split(',') if u.strip()] # Se forem strings, retira os colchetes e espaços, depois separa por virgula
    else: 
        ValueError(Urls)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file= '../.env',
        env_ignore_empty=False,
        extra='ignore'
    )

    HOSTS: Annotated[list[AnyUrl] | str, BeforeValidator(cors_config)] = []
    COMMONS_URLS:list[str] = ["http://localhost","http://localhost:5500","http://127.0.0.1","http://127.0.0.1:5500","http://127.0.0.1:8000"]

    @computed_field
    @property
    def sanatize_cors(self) -> list[str]:
        return [str(origins) for origins in self.HOSTS] + self.COMMONS_URLS # type: ignore
    
    
    DB_PATH: Path = Path("/app/data/key.db")
    API_KEY: str
    
    SENDER: EmailStr | None = None
    PASS: str | None = None
    SMTP_SERVER: str | str='smtp.gmail.com'
    PORT_SMTP: int = 465
    EHELO: str | str ='localhost'
    MSG_PATH: Path = Path("/home/kevyn/PycharmProjects/Email_Sender/Assets/mensagem.txt")
    SUBJECT: str | str=""

    QTD_EMAILS: int = 10
    TMP_EMAILS: int = 60
    TMP_BLOQ: int = 30
    
    def path_validator(self):

        if self.MSG_PATH == None:
            raise HTTPException(status_code=500, detail=f'MSG_PATH não definido')
        
        filePath = self.MSG_PATH
        if not filePath.is_file(): # type: ignore
            raise HTTPException(status_code=500, detail=f'Diretório não encontrado: {filePath}')
        else:
            return filePath


    PROJECT_NAME:str = 'FastAPI E-mail Sender'
    DESCRIPTION:str = 'A modular FastAPI program to send e-mails with smtp protocol'


    
settings = Settings() # type: ignore
