import re

from pydantic import BaseModel, EmailStr


class MailConfig(BaseModel):
    """Configuração opcional de envio informada pelo dev consumidor da API."""

    sender: EmailStr | None = None
    password: str | None = None
    smtp_server: str | None = None
    port_smtp: int | None = None
    ehelo: str | None = None
    subject: str | None = None
    template: str | None = None


class baseUser(BaseModel):
    userMail: EmailStr
    userName: str
    config: MailConfig | None = None

    def SanitizeName(self) -> str:
        userName = re.sub(r"[^A-Za-zÀ-ÖØ-öø-ÿ\s]", " ", self.userName).strip()
        return " ".join(userName.split())  # remove múltiplos espaços
