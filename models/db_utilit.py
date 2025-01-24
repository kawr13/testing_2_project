from aiogram.types import Message

from models.model import User


async def get_user(tg_id: int) -> User:
    user, created = await User.get_or_create(tg_id=tg_id)
    return user


async def is_admin(message: Message) -> bool:
    user = await get_user(message.chat.id)
    return user.is_admin


async def is_active(message: Message = None,) -> bool:
    if message:
        user = await get_user(message.chat.id)
        return user.is_active


async def set_active( tg_id: int = None, is_activ: bool = None) -> None:
    user = await User.filter(tg_id=tg_id).first()
    user.is_active = is_activ
    await user.save()