from fastapi import FastAPI, File, Form, HTTPException, Depends, FastAPI, Request, Query
from typing import Union
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
import service
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from base import get_session
from fastapi_pagination import Page, add_pagination, paginate
from typing_extensions import Annotated
import secrets
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from token2 import create_jwt_token, verify_jwt_token
from models import User

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory="templates")

async def hash_password(password: str):
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
    token: Union[str, None] = None
    remember_me: bool
    product_list: Union[str, None] = None
    date_registr: Union[str, None] = None
    
    def add_data(self, data: dict):
        self.__dict__.update(data)

class UserAuth(BaseModel):
    email: str
    password: str

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


@app.post('/register', response_model=UserSchema)
async def register_token(user: UserSchema, session: AsyncSession=Depends(get_session)):
    token = secrets.token_hex(16)
    hashed_password = await hash_password(user.password)
    data = {
        'password': hashed_password,
        'token': token
    }
    user.add_data(data)
    add_user = await service.register_user(session, name=user.name, phone=user.phone, email=user.email, 
                                        password=user.password, remember_me=user.remember_me, 
                                        token=user.token)
    print(user.token)
    await session.commit()
    return user

@app.get('/register/{token}')
async def finish_register(token: str,  session: AsyncSession=Depends(get_session)):
    user = await service.get_user(session, token)
    try:
        user = user[0][0]
        if user.token == token:
            user = await service.activate_user(session, token)
            await session.commit()
            return 'Регистрация подтверждена'
        else:
            return 'Ошибка 404'
    except Exception:
        return 'Ошибка 404'

@app.get('/login', response_class=HTMLResponse)
async def login(request: Request, session: AsyncSession=Depends(get_session)):
    return templates.TemplateResponse('login.html', {'request': request})

@app.post('/login')
async def auth_login(user: UserAuth, session: AsyncSession=Depends(get_session)):
    user_sql = await service.get_user_login(session, user.email)
    is_password_correct = pwd_context.verify(user.password, user_sql[0].password)
    jwt_token = create_jwt_token({"sub": user_sql[0].email})
    return {"access_token": jwt_token, "token_type": "bearer", 
            'user_id': user_sql[0].id, 'email': user_sql[0].email }

async def get_current_user(session: AsyncSession=Depends(get_session)):
    decoded_data = verify_jwt_token('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ2bGFkQGdtYWlsLmNvbSIsImV4cCI6MTcwMzYyMTYwM30.ihBUroopDb_EQxNITQy2_z2guDPUJOZuQ1MqZ1OFW_k')
    print(decoded_data)
    if not decoded_data:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = await service.get_user_login(session, decoded_data["sub"])  # Получите пользователя из базы данных
    return user

@app.get("/users/me")
async def get_user_me(current_user: str = Depends(get_current_user)):
    return current_user