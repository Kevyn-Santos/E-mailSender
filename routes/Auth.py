from fastapi import APIRouter, HTTPException, status

from core.security import Jwt
from core.settings import settings
from models.authModules import LoginRequest, TokenResponse

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/token", response_model=TokenResponse)
async def login(credentials: LoginRequest) -> TokenResponse:
    if credentials.username != settings.API_USER or credentials.password != settings.API_PASS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = Jwt.create_token(data={"sub": credentials.username})
    return TokenResponse(access_token=token)
