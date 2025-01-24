import jwt
import datetime
from fastapi import Depends, HTTPException, Security, APIRouter
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from models.model import User
from dotenv import load_dotenv
import os

load_dotenv()
router = APIRouter(
    prefix="",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)


SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
TOKEN_EXPIRATION_MINUTES = 60
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="get-token")


security = HTTPBearer()

def create_token(user_id: int):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=TOKEN_EXPIRATION_MINUTES)
    payload = {
        "sub": user_id,
        "exp": expiration
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Функция для получения пользователя по токену
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        # Декодируем токен
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        is_admin = payload.get("is_admin")

        if is_admin is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        return is_admin  # Возвращаем флаг админа (True/False)

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


# Функция для проверки, является ли пользователь админом
async def is_admin(is_admin: bool = Depends(get_current_user)):
    if not is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not admin")
    return True  # Возвращаем True, если пользователь админ


class UserId(BaseModel):
    user_id: int


@router.post('/get-token/')
async def get_token(data: UserId):
    token = create_token(data.user_id)
    return {"token": token}


@router.get("/protected/")
def protected_route(user_id: int = Depends(verify_token)):
    return {"message": "Access granted", "user_id": user_id}