from fastapi import APIRouter, BackgroundTasks, Request, Depends
from src.core.security import Rate_limiter, verify_header_key
from src.models.emailModules import baseUser
from src.services.sendMail import sendMail

routers = APIRouter(tags=['SendEmail'])

@routers.post('/sendMail')
@Rate_limiter.limiter.limit(Rate_limiter.get_rate_limit_string)
async def email_sender(User: baseUser, 
                       background: BackgroundTasks, 
                       request: Request,
                       _: str = Depends(verify_header_key)):
    background.add_task(sendMail, to=User.userMail, name=User.userName)
