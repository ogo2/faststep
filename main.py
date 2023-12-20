from fastapi import FastAPI, File, Form
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
from typing_extensions import Annotated
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

class ProductSchema(BaseModel):
    name: str
    photo_path: str
    price: int
    old_price: int
    url_product: str
    sex: str

class UserSchema(BaseModel):
    name: str
    phone: str
    email: str
    password: str
    product_list: list
    date_registr: str


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
    return templates.TemplateResponse("shop.html", {"request": request, 'products': products, 'brand': data_brand, 'product_all': int(list_all), 'dictionary': dictionary, 'page': page})

@app.get('/shoes/{name_product}/{id_product}', response_class=HTMLResponse, response_model=List[ProductSchema])
async def product_page(name_product: str, id_product: int,  request: Request, session: AsyncSession=Depends(get_session)):
    product = await service.get_product_page(session, id_product)
    return templates.TemplateResponse("product-page.html", {"request": request, 'product': product, 'name_product': name_product})

@app.get('/login', response_class=HTMLResponse)
async def login(request: Request, session: AsyncSession=Depends(get_session)):
    return templates.TemplateResponse('login.html', {'request': request})

@app.get('/register', response_class=HTMLResponse)
async def register(request: Request, session: AsyncSession=Depends(get_session)):
    return templates.TemplateResponse('register.html', {'request': request})


@app.post('/register')
async def register_user(username: str = Form(), password: str = Form()):
    hashed_password = hash_password(password)
    return {"username": username, 'hashed_password': hashed_password}