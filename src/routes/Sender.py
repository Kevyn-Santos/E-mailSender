from fastapi import APIRouter, BackgroundTasks, Request
from src.core.security import Rate_limiter
from src.models.emailModules import baseUser
from src.services.sendMail import sendMail

routers = APIRouter(tags=['SendEmail'])

@routers.post('/sendMail')
@Rate_limiter.limiter.limit(Rate_limiter.get_rate_limit_string)
async def email_sender(User: baseUser, background: BackgroundTasks, request: Request):
    background.add_task(sendMail, to=User.userMail, name=User.userName)
