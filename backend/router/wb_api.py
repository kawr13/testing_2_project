import pytz
from fastapi import Depends, HTTPException, Security, APIRouter
from fastapi import Depends, HTTPException, status
from icecream import ic
from pydantic import BaseModel

from backend.router.auth import verify_token
from backend.shemas.product_shemas import ProductResponse, ProductCreate, ArticularResponse
from backend.shemas.user_shemas import UserTgId, UserTgIdOut
from models.db_utilit import get_user, set_active, add_product, get_product, update_product
from models.model import User
from dotenv import load_dotenv
import os

from wb_parsing import WBParser

load_dotenv()

router = APIRouter(
    prefix="",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)


@router.post('/api/v1/products/', response_model=ProductResponse)
async def products_view(data: ArticularResponse, user_id: int = Depends(verify_token)):
    artikul = data.artikul
    product_bd = await get_product(artikul)
    response = await WBParser.parse_product(artikul)
    product = ProductResponse(**response)
    ic(product)
    if product_bd:
        product_bd.artikul = product.artikul
        product_bd.name = product.name
        product_bd.price = product.price
        product_bd.rating = product.rating
        product_bd.total_quantity = product.total_quantity
        moscow_tz = pytz.timezone('Europe/Moscow')
        product_bd.last_update = product.last_update.astimezone(moscow_tz).replace(tzinfo=None)
        await update_product([product_bd])
    else:
        await add_product(product)
    return product


@router.get('/api/v1/subscribe/')
async def products_view(artikul: int, user_id: int = Depends(verify_token)):
    product_bd = await get_product(artikul)
    response = await WBParser.parse_product(str(artikul))
    product = ProductResponse(**response)
    ic(product)
    if product_bd:
        product_bd.artikul = product.artikul
        product_bd.name = product.name
        product_bd.price = product.price
        product_bd.rating = product.rating
        product_bd.total_quantity = product.total_quantity
        moscow_tz = pytz.timezone('Europe/Moscow')
        product_bd.last_update = product.last_update.astimezone(moscow_tz).replace(tzinfo=None)
        product_bd.is_update = True if product_bd.is_update is False else False
        await update_product([product_bd])
    else:
        await add_product(product)
    return product