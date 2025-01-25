import asyncio
from typing import Dict, Any

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from icecream import ic
from pytz import timezone

from backend.shemas.product_shemas import ProductResponse
from db_conf import AsyncSessionLocal
from models.db_utilit import get_all_product, update_product
from wb_parsing import WBParser


async def shedul_pars_wb():
    ic('shedul_pars_wb START')
    product_bd = await get_all_product()

    semaphore = asyncio.Semaphore(10)

    async def parse_and_update(product):
        async with semaphore:
            response = await WBParser.parse_product(product.artikul)
            parsed_product = ProductResponse(**response)

            moscow_tz = pytz.timezone('Europe/Moscow')
            parsed_product.last_update = parsed_product.last_update.astimezone(moscow_tz).replace(tzinfo=None)

            product.artikul = parsed_product.artikul
            product.name = parsed_product.name
            product.price = parsed_product.price
            product.rating = parsed_product.rating
            product.total_quantity = parsed_product.total_quantity
            product.last_update = parsed_product.last_update

            return product

    tasks = [parse_and_update(product) for product in product_bd]
    updated_products = await asyncio.gather(*tasks)


    await update_product(updated_products)




scheduler = AsyncIOScheduler()


moscow_tz = timezone('Europe/Moscow')

scheduler.add_job(shedul_pars_wb, IntervalTrigger(minutes=30))