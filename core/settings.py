from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import (EmailStr, AnyUrl, BeforeValidator, computed_field)
from fastapi import HTTPException
from typing import Annotated, Any
from pathlib import Path


def cors_config(Urls: Any) -> list[str] | str:
    if isinstance(Urls, str) and Urls.startswith('['):
        return[e.strip() for e in Urls.split(',') if e.strip()]
    elif isinstance(Urls, list | str):
        return Urls
    else: 
        ValueError(Urls)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file= '../Assets/.env',
        env_ignore_empty=False,
        extra='ignore'
    )

    HOSTS: Annotated[list[AnyUrl] | str, BeforeValidator(cors_config)]
    COMMONS_URLS:list[str] = ["http://localhost","http://localhost:5500","http://127.0.0.1","http://127.0.0.1:5500","http://127.0.0.1:8000"]

    @computed_field
    @property
    def sanatize_cors(self) -> list[str]:
        return [str(origins).rstrip(',') for origins in self.HOSTS] + [self.COMMONS_URLS] # type: ignore
    
    
    
    SENDER: EmailStr | None = None
    PASS: str | None = None
    SMTP_SERVER: str | str='smtp.gmail.com'
    PORT_SMTP: int = 465
    EHELO: str | str ='localhost'
    MSG_PATH: Path
    SUBJECT: str | str=""
    
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
