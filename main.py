from fastapi import FastAPI, File, Form, HTTPException, Depends, FastAPI, Request, Query, Cookie, Response, status
from typing import Union
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
import service
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from base import get_session
from fastapi_pagination import Page, add_pagination, paginate
from typing_extensions import Annotated
import secrets
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from token2 import create_jwt_token, verify_jwt_token
from models import User
from jose import JWTError, jwt


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
    activate: Union[str, None] = None
    remember_me: bool
    product_list: Union[str, None] = None
    date_registr: Union[str, None] = None
    
    def add_data(self, data: dict):
        self.__dict__.update(data)

class UserAuth(BaseModel):
    email: str
    password: str

async def get_current_user(jwt_token: str = Cookie(), session: AsyncSession=Depends(get_session)):
    try:
        decoded_data = verify_jwt_token(jwt_token)
        if not decoded_data:
            return None                 #токен есть но у него закончилось время, пользователь не вышел
        user = await service.get_user_login(session, decoded_data["sub"])  # Получите пользователя из базы данных
        return user
    except Exception:
        return None 
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
async def product_list(request: Request, session: AsyncSession=Depends(get_session), page: int = 1, current_user: dict = Depends(get_current_user)):
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
    return templates.TemplateResponse("shop.html", {"request": request, 'products': products, 
                                                    'brand': data_brand, 'product_all': int(list_all), 
                                                    'dictionary': dictionary, 'page': page, 'current_user': current_user})

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
        'activate': token
    }
    user.add_data(data)
    add_user = await service.register_user(session, name=user.name, phone=user.phone, email=user.email, 
                                        password=user.password, remember_me=user.remember_me, 
                                        token=user.activate)
    await session.commit()
    print(token)
    return user

@app.get('/register/{activate}')
async def finish_register(activate: str,  session: AsyncSession=Depends(get_session)):
    user = await service.get_user(session, activate)
    try:
        user = user[0][0]
        if user.activate == activate:
            user = await service.activate_user(session, activate)
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
async def auth_login(response: Response, user: UserAuth, session: AsyncSession=Depends(get_session) ):
    
    user_sql = await service.get_user_login(session, user.email)
    user_sql = user_sql[0]
    if user_sql.activate != 'activate':
        return 'Не подтвержденный профиль!!!'
    is_password_correct = pwd_context.verify(user.password, user_sql.password)
    jwt_token = create_jwt_token({"sub": user_sql.email})
    response.set_cookie(key="jwt_token", value=jwt_token)
    return {"access_token": jwt_token, "token_type": "bearer", 
            'user_id': user_sql.id, 'email': user_sql.email }

@app.get('/logout')
async def logout(response: Response):
    response.delete_cookie("jwt_token")
    return response, RedirectResponse(url="/shoes")


@app.get("/users/me")
async def get_user_me(current_user: dict = Depends(get_current_user)):
    return current_user