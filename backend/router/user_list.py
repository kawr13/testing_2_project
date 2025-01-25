from fastapi import Depends, HTTPException, Security, APIRouter
from fastapi import Depends, HTTPException, status
from pydantic import BaseModel

from backend.router.auth import verify_token
from backend.shemas.user_shemas import UserTgId, UserTgIdOut
from models.db_utilit import get_user, set_active
from models.model import User
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter(
    prefix="",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)


@router.post('/api/vite-list/')
async def vite_list(data: UserTgId, user_id: int = Depends(verify_token)):
    tg_id = data.tg_id
    is_active = data.is_active
    result = await set_active(tg_id=tg_id, is_activ=is_active)
    return UserTgIdOut(tg_id=tg_id, is_active=is_active)