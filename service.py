from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from models import *
from typing import List, Union
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

async def get_user(session: AsyncSession, activate: str) -> List['User']:
    result = await session.execute(select(User).where(User.activate==activate))
    return result.all()

async def get_user_login(session: AsyncSession, email: str) -> List['User']:
    result = await session.execute(select(User).where(User.email==email))
    return result.scalars().all()

async def register_user(session: AsyncSession, name: str, phone: str, 
                        email: str, password: str, subscribe: bool, token: str)->List['User']:
    new_user = User(name=name,
                    phone=phone,
                    email=email,
                    password=password,
                    subscribe=subscribe,
                    date_registr=datetime.now(),
                    activate=token)
    session.add(new_user)
    return new_user


async def activate_user(session: AsyncSession, activate: str):
    activate_user = await session.execute(update(User).where(User.activate == activate).values(activate='activate'))
    return activate_user

async def subscribe_me_up(session: AsyncSession, email: str):
    subscribe_user = await session.execute(update(User).where(User.email == email).values(subscribe=True))
    return subscribe_user

async def add_token(session: AsyncSession, token: str, email: str):
    add_token = await session.execute(update(User).where(User.email==email).values(token=token))
    return add_token

async def add_wish(session: AsyncSession, email: str, product_wish: dict):
    add_wish = await session.execute(update(User).where(User.email==email).values(product_list=product_wish))
    return add_wish

async def get_brand_name(session: AsyncSession) -> List['Product']:
    result = await session.execute(select(func.lower(Product.brand), func.count(func.lower(Product.brand)).label("brand_count")).group_by(func.lower(Product.brand)).order_by(func.count(func.lower(Product.brand)).desc()))
    data = result.all()
    for i in range(len(data)):
        data[i] = list(data[i])
        if data[i][0][0] == "'":
            data[i][0] = data[i][0].strip("''")
    return data

# фильтры
async def get_filter_prod(session: AsyncSession, skip, limit, select_item: str, brand: Union[dict, None] = None, 
                          price: Union[dict, None] = None):
    if select_item == 'new':
        if brand and price:
            result = await session.execute(select(Product).where(Product.price.between(int(price[0]), int(price[1])), func.lower(Product.brand).in_(brand)).order_by(Product.date.desc()).offset(skip).limit(limit))
            return result.scalars().all()
        if brand:
            result = await session.execute(select(Product).where(func.lower(Product.brand).in_(brand)).order_by(Product.date.desc()).offset(skip).limit(limit))
            return result.scalars().all()
        if price:
            result = await session.execute(select(Product).where(Product.price.between(int(price[0]), int(price[1]))).order_by(Product.date.desc()).offset(skip).limit(limit)) 
            return result.scalars().all()
        result = await session.execute(select(Product).order_by(Product.date.desc()).offset(skip).limit(limit)) 
        return result.scalars().all()
    if select_item == 'min':
        if brand and price:
            result = await session.execute(select(Product).where(Product.price.between(int(price[0]), int(price[1])), func.lower(Product.brand).in_(brand)).order_by(Product.price.asc()).offset(skip).limit(limit))
            return result.scalars().all()
        if brand:
            result = await session.execute(select(Product).where(func.lower(Product.brand).in_(brand)).order_by(Product.price.asc()).offset(skip).limit(limit))
            return result.scalars().all()
        if price:
            result = await session.execute(select(Product).where(Product.price.between(int(price[0]), int(price[1]))).order_by(Product.price.asc()).offset(skip).limit(limit)) 
            return result.scalars().all()
        result = await session.execute(select(Product).order_by(Product.price.asc()).offset(skip).limit(limit)) 
        return result.scalars().all()
    if select_item == 'max':
        if brand and price:
            result = await session.execute(select(Product).where(Product.price.between(int(price[0]), int(price[1])), func.lower(Product.brand).in_(brand)).order_by(Product.price.desc()).offset(skip).limit(limit)) 
            return result.scalars().all()
        if brand:
            result = await session.execute(select(Product).where(func.lower(Product.brand).in_(brand)).order_by(Product.price.desc()).offset(skip).limit(limit))
            return result.scalars().all()
        if price:
            result = await session.execute(select(Product).where(Product.price.between(int(price[0]), int(price[1]))).order_by(Product.price.desc()).offset(skip).limit(limit)) 
            return result.scalars().all()
        result = await session.execute(select(Product).order_by(Product.price.desc()).offset(skip).limit(limit)) 
        return result.scalars().all()
    
async def get_filter_prod_all(session: AsyncSession, select_item: str, brand: Union[dict, None] = None, 
                          price: Union[dict, None] = None):
    if select_item == 'new':
        if brand and price:
            result = await session.execute(select(Product).where(Product.price.between(int(price[0]), int(price[1])), func.lower(Product.brand).in_(brand)).order_by(Product.date.desc()))
            return result.scalars().all()
        if brand:
            result = await session.execute(select(Product).where(func.lower(Product.brand).in_(brand)).order_by(Product.date.desc()))
            return result.scalars().all()
        if price:
            result = await session.execute(select(Product).where(Product.price.between(int(price[0]), int(price[1]))).order_by(Product.date.desc())) 
            return result.scalars().all()
        result = await session.execute(select(Product).order_by(Product.date.desc())) 
        return result.scalars().all()
    if select_item == 'min':
        if brand and price:
            result = await session.execute(select(Product).where(Product.price.between(int(price[0]), int(price[1])), func.lower(Product.brand).in_(brand)).order_by(Product.price.asc()))
            return result.scalars().all()
        if brand:
            result = await session.execute(select(Product).where(func.lower(Product.brand).in_(brand)).order_by(Product.price.asc()))
            return result.scalars().all()
        if price:
            result = await session.execute(select(Product).where(Product.price.between(int(price[0]), int(price[1]))).order_by(Product.price.asc())) 
            return result.scalars().all()
        result = await session.execute(select(Product).order_by(Product.price.asc())) 
        return result.scalars().all()
    if select_item == 'max':
        if brand and price:
            result = await session.execute(select(Product).where(Product.price.between(int(price[0]), int(price[1])), func.lower(Product.brand).in_(brand)).order_by(Product.price.desc())) 
            return result.scalars().all()
        if brand:
            result = await session.execute(select(Product).where(func.lower(Product.brand).in_(brand)).order_by(Product.price.desc()))
            return result.scalars().all()
        if price:
            result = await session.execute(select(Product).where(Product.price.between(int(price[0]), int(price[1]))).order_by(Product.price.desc())) 
            return result.scalars().all()
        result = await session.execute(select(Product).order_by(Product.price.desc())) 
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