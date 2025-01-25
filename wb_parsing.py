import httpx
import logging
from utilities.icream import ic, log

class WBParser:
    @staticmethod
    async def parse_product(artikul: str):
        url = f"https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&spp=30&nm={artikul}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                ic(response.json())
                data = response.json()
                
                product_info = data['data']['products'][0]  
                
                return {
                    'artikul': artikul,
                    'name': product_info.get('name', 'Без названия'),
                    'price': int(product_info.get('salePriceU', 0)) / 100,
                    'rating': product_info.get('rating', 0),
                    'total_quantity': sum(map(lambda size: size.get('qty', 0), product_info.get('sizes', [{}])[0].get('stocks', [0]))),
                }
                
        
        except Exception as e:
            logging.error(f"Ошибка парсинга: {e}")
            return None
        

async def main():
    art: str = '211695539'
    data = await WBParser.parse_product(art)
    log.info(data)
    
    
if __name__ == '__main__':
    import asyncio
    asyncio.run(main())