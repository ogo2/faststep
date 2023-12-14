from fastapi import FastAPI
from typing import Union
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError
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
    return [ProductSchema(name=c.name, photo_path=c.photo_path, price=c.price, old_price=c.old_price, url_product=c.url_product, sex=c.sex) for c in products]
# сессия может быть внедрена (инжектирована) с помощью Depends. Таким образом, вызов каждого из маршрутов создаст новую сессию. 
# Для получения данных единственное изменение заключается в том, что теперь мы хотим применить await для нашей сервисной функции.
@app.post('/admin/add/')
async def add_product(product: ProductSchema, session: AsyncSession = Depends(get_session)): 
    product = service.add_product(session, product.name, product.photo_path, product.price, product.old_price, product.url_product, product.sex)
    await session.commit()
    return product
    
@app.get("/", response_class=HTMLResponse, response_model=List[ProductSchema])
async def index(request: Request, session: AsyncSession = Depends(get_session)):
    products = await service.get_product(session)
    return templates.TemplateResponse("index.html", {"request": request, 'products': products})

@app.get('/admin', response_class=HTMLResponse)
async def add_product_page(request: Request):
    return templates.TemplateResponse("admin.html", {'request': request})
