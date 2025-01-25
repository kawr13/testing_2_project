from icecream import ic
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message

from backend.shemas.product_shemas import ProductResponse
from models.model import User, Product  # Импортируем модель User
from db_conf import get_async_session, AsyncSessionLocal
from typing import Optional


# Получение пользователя по tg_id или создание нового
async def get_user(tg_id: int) -> User:
    async with AsyncSessionLocal() as session:  # Используем async for вместо async with
        result = await session.execute(select(User).filter(User.tg_id == str(tg_id)))
        user = result.scalars().first()
        ic(user)

        if not user:
            user = User(tg_id=str(tg_id))
            session.add(user)
            await session.commit()

    return user


async def add_user(tg_id: int=None, is_admin: bool=False, is_active: bool=False) -> User:
    user = User(tg_id=str(tg_id), is_admin=is_admin, is_active=is_active)
    async with AsyncSessionLocal() as session:
        session.add(user)
        await session.commit()
    return user


async def update_user(user: User) -> User:
    async with AsyncSessionLocal() as session:
        session.add(user)
        await session.commit()
    return user


async def get_admins() -> list:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).filter(User.is_admin == True))
        admins = result.scalars().all()
    return admins


async def get_all_users() -> list:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).filter(User.is_admin == False))
        admins = result.scalars().all()
    return admins




# Проверка, является ли пользователь администратором
async def is_admin(message: Message) -> bool:
    user = await get_user(message.chat.id)
    return user.is_admin


# Проверка, активен ли пользователь
async def is_active(message: Optional[Message] = None) -> bool:
    if message:
        user = await get_user(message.chat.id)
        return user.is_active
    return False


# Установка статуса активности пользователя
async def set_active(tg_id: int, is_activ: bool) -> None:
    async with AsyncSessionLocal() as session:

        result = await session.execute(select(User).filter(User.tg_id == str(tg_id)))
        user = result.scalars().first()

        if user:
            user.is_active = is_activ
            await session.commit()


async def get_product(article: int) -> User:
    async with AsyncSessionLocal() as session:  # Используем async for вместо async with
        result = await session.execute(select(Product).filter(Product.artikul == str(article)))
        product = result.scalars().first()


        if not product:
            return None

    return product


async def add_product(product: ProductResponse) -> Product:
    product = Product(
        artikul=product.artikul,
        name=product.name,
        price=product.price,
        rating=product.rating,
        total_quantity=product.total_quantity,
        is_update=True
    )
    async with AsyncSessionLocal() as session:
        session.add(product)
        await session.commit()
    return product


async def update_product(products: list):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            for product in products:
                session.add(product)  # Добавляем все товары в сессию
        await session.commit()  # Один общий коммит для всех товаров


async def get_all_product() -> list:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Product).filter(Product.is_update == True))
        products = result.scalars().all()
    return products