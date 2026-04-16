from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Request

from core.security import Jwt, get_rate_limit_string, limiter
from models.emailModules import baseUser
from services.sendMail import sendMail

routers = APIRouter(tags=['SendEmail'])


@routers.post('/sendMail')
@limiter.limit(get_rate_limit_string)
async def email_sender(
    User: baseUser,
    background: BackgroundTasks,
    request: Request,
    _current_user: Annotated[dict, Depends(Jwt.get_current_user)],
):
    background.add_task(sendMail, to=User.userMail, name=User.userName)
