from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import *
from typing import List
# Выводим товар из бд
async def get_product(session: AsyncSession) -> List['Product']:
    result = await session.execute(select(Product).limit(10))
    return result.scalars().all()

# Функция add_product просто помещает новый объект Product в сессию — мы будем управлять транзакцией в контроллере (маршрут).
def add_product(session: AsyncSession, 
             name: str, photo_path: str, price: float,
             old_price: float, url_product: str, sex: str):
    new_product = Product(
        name=name, 
        photo_path=photo_path,
        price=price,
        old_price=old_price,
        url_product=url_product,
        sex=sex)
    session.add(new_product)
    return new_product