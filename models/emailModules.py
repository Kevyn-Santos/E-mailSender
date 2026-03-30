from pydantic import (BaseModel, EmailStr)
import re

class baseUser(BaseModel):
    userMail: EmailStr
    userName: str
    def SanitizeName(self):
        userName = re.sub(r"[^A-Za-zÀ-ÖØ-öø-ÿ\s]", " ", self.userMail).strip()
        return " ".join(userName.split())  # remove múltiplos espaços
