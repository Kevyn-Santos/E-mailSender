from fastapi import (APIRouter, BackgroundTasks)
from models.emailModules import baseUser
from services.sendMail import sendMail

routers = APIRouter(tags=['SendEmail'])

@routers.post('/sendMail')
def email_sender(User: baseUser, background: BackgroundTasks):
    background.add_task(sendMail, to=User.userMail, name=User.userName)    