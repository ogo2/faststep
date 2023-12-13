from fastapi import FastAPI
from typing import Union
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import service
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from fastapi import Depends
from base import get_session
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

class ProductSchema(BaseModel):
    name: str
    photo_path: str
    price: float
    old_price: float
    url_product: str
    sex: str

@app.get("/product", response_model=List[ProductSchema])
async def get_biggest_cities(session: AsyncSession = Depends(get_session)):
    products = await service.get_product(session)
    return [ProductSchema(name=c.name) for c in products]

# @app.get('/admin/add/')
# async def new_product(product: ProductSchema):
#     return product(name='Licka',
#                    photo_path='https://s7d2.scene7.com/is/image/aeo/0414_6176_256_of?$pdp-m-opt$',
#                    price=12.2,
#                    old_price=22.1,
#                    url_product='https://www.ae.com/ca/en/p/women/shoes/sneakers/ae-embroidered-platform-sneaker/0414_6176_256?menu=cat4840004',
#                    sex='men')

# сессия может быть внедрена (инжектирована) с помощью Depends. Таким образом, вызов каждого из маршрутов создаст новую сессию. 
# Для получения данных единственное изменение заключается в том, что теперь мы хотим применить await для нашей сервисной функции.
@app.post('/admin/add/')
async def add_product(product: ProductSchema, session: AsyncSession = Depends(get_session)): 
    product = service.add_product(session, product.name, product.photo_path, product.price, product.old_price, product.url_product, product.sex)
    try:
        await session.commit()
        return product
    except IntegrityError as ex:
        await session.rollback()
        raise DuplicatedEntryError("Ошибка")
    
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})