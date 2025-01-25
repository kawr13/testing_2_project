from pydantic import BaseModel


class UserTgId(BaseModel):
    tg_id: int
    is_active: bool


class UserTgIdOut(BaseModel):
    tg_id: int
    is_active: bool