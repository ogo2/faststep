from fastapi import FastAPI
from typing import Union
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request, Query
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
from fastapi_pagination import Page, add_pagination, paginate

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

# cтраница с кроссовками
@app.get('/shoes', response_class=HTMLResponse, response_model=List[ProductSchema])
async def product_list(request: Request, session: AsyncSession=Depends(get_session), page: int = 1):
    
    # if page == 1:
    #     skip = 0
    #     limit = 12
    # elif page>1:
    #     skip = page * 12
    #     limit = 12
    dictionary = {}
    limit = 12
    for i in range(1, 100): 
        if i == 1:
            dictionary[i] = 0
        else:
            dictionary[i] = dictionary[i-1] + 12
            
    products = await service.get_product_pag(session, dictionary[page], limit)
    print(dictionary[page])

            
    products_all = await service.get_product_all(session)
    data_brand = await service.get_brand_name(session)
    list_all = len(products_all) / 12
    # count_brand = await service.get_product_count(session)
    return templates.TemplateResponse("shop.html", {"request": request, 'products': products, 'brand': data_brand, 'product_all': int(list_all), 'dictionary': dictionary, 'page': page})


@app.get('/shoes/{name_product}/{id_product}', response_class=HTMLResponse, response_model=List[ProductSchema])
async def product_page(name_product: str, id_product: int,  request: Request, session: AsyncSession=Depends(get_session)):
    product = await service.get_product_page(session, id_product)
    return templates.TemplateResponse("product-page.html", {"request": request, 'product': product, 'name_product': name_product})

@app.get('/admin', response_class=HTMLResponse)
async def add_product_page(request: Request):
    return templates.TemplateResponse("admin.html", {'request': request})


