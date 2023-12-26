from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from models import *
from typing import List
from sqlalchemy import func
from datetime import datetime


# Выводим товар из бд
async def get_product(session: AsyncSession) -> List['Product']:
    result = await session.execute(select(Product).limit(12))
    return result.scalars().all()

async def get_product_pag(session: AsyncSession, skip, limit) -> List['Product']:
    result = await session.execute(select(Product).offset(skip).limit(limit))
    return result.scalars().all()

async def get_product_all(session: AsyncSession) -> List['Product']:
    result = await session.execute(select(Product))
    return result.scalars().all()

async def get_product_page(session: AsyncSession, id: int) -> List['Product']:
    result = await session.execute(select(Product).where(Product.id==id))
    return result.scalars().all()

async def get_user(session: AsyncSession, token: str) -> List['User']:
    result = await session.execute(select(User).where(User.token==token))
    return result.all()

async def get_user_login(session: AsyncSession, email: str) -> List['User']:
    result = await session.execute(select(User).where(User.email==email))
    return result.scalars().all()

async def register_user(session: AsyncSession, name: str, phone: str, 
                        email: str, password: str, remember_me: bool, token: str)->List['User']:
    new_user = User(name=name,
                    phone=phone,
                    email=email,
                    password=password,
                    remember_me=remember_me,
                    date_registr=datetime.now(),
                    token=token)
    session.add(new_user)
    return new_user

async def activate_user(session: AsyncSession, token: str):
    activate_user = await session.execute(update(User).where(User.token == token).values(token='activate'))
    return activate_user

async def get_brand_name(session: AsyncSession) -> List['Product']:
    result = await session.execute(select(Product.brand, func.count(Product.brand).label("brand_count")).group_by(Product.brand).order_by(func.count(Product.brand).desc()))
    data = result.all()
    for i in range(len(data)):
        data[i] = list(data[i])
        if data[i][0][0] == "'":
            data[i][0] = data[i][0].strip("''")
    return data

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