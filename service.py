from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import *
from typing import List
from sqlalchemy import func

# Выводим товар из бд
async def get_product(session: AsyncSession) -> List['Product']:
    result = await session.execute(select(Product).limit(12))
    return result.scalars().all()

async def get_product_page(session: AsyncSession, id: int) -> List['Product']:
    result = await session.execute(select(Product).where(Product.id==id))
    return result.scalars().all()

async def get_brand_name(session: AsyncSession) -> List['Product']:
    result = await session.execute(select([func.count(Product.brand)], Product.brand)).group_by(Product.brand)
    print(result.scalars().all() )
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