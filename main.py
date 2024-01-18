from fastapi import FastAPI, File, Form, HTTPException, Depends, FastAPI, Request, Query, Cookie, Response, status, Security
from typing import Union
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel
import service
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from base import get_session
from fastapi_pagination import Page, add_pagination, paginate
from typing_extensions import Annotated
import secrets
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from token2 import create_jwt_token, verify_jwt_token
from models import User
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt


app = FastAPI()
security = HTTPBearer()
app.mount("/static", StaticFiles(directory="static"), name="static")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory="templates")
# Добавьте эти настройки, чтобы разрешить запросы от вашего сайта Ajax
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
async def hash_password(password: str):
    return pwd_context.hash(password)

class ProductWish(BaseModel):
    id_product: Union[int, str]

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
    subscribe: bool
    product_list: Union[str, None] = None
    date_registr: Union[str, None] = None
    
    def add_data(self, data: dict):
        self.__dict__.update(data)

class UserAuth(BaseModel):
    email: str
    password: str

async def get_current_user(request: Request, session: AsyncSession=Depends(get_session)):
    try:
        decoded_data = verify_jwt_token(request.cookies.get("jwt_token"))
        if not decoded_data:
            return None                 #токен есть но у него закончилось время, пользователь не вышел
        user = await service.get_user_login(session, decoded_data["sub"])  # Получите пользователя из базы данных
        return user
    except Exception:
        return None 

@app.get("/", response_class=HTMLResponse, response_model=List[ProductSchema])
async def index(request: Request, session: AsyncSession = Depends(get_session), 
                current_user: dict = Depends(get_current_user)):
    products = await service.get_product(session)
    products_all = await service.get_product_all(session)
    return templates.TemplateResponse("index.html", {"request": request, 'products': products, 'products_all': products_all,
                                                     'current_user': current_user})

# cтраница с кроссовками
@app.get('/shoes', response_class=HTMLResponse, response_model=List[ProductSchema])
async def product_list(request: Request, session: AsyncSession=Depends(get_session), page: int = 1, 
                       current_user: dict = Depends(get_current_user)):
    dictionary = {}             #словарь с кол-вом страниц и кол-вом товара который нужно пропустить  при sql запросе (skip)
    limit = 12
    for i in range(1, 100): 
        if i == 1:
            dictionary[i] = 0
        else:
            dictionary[i] = dictionary[i-1] + 12
            
    products = await service.get_product_pag(session, dictionary[page], limit)      #sql запрос который пропускает (skip) и выводит нужное кол-во товара (limit)
    products_all = await service.get_product_all(session)   
    data_brand = await service.get_brand_name(session)
    list_all = len(products_all) / 12           #считает кол-во страниц
    return templates.TemplateResponse("shop.html", {"request": request, 'products': products, 
                                                    'brand': data_brand, 'product_all': int(list_all), 'products_all': products_all,
                                                    'dictionary': dictionary, 'page': page, 'current_user': current_user})
# обработка фильтра на странице с кросовками
@app.get('/shoes/filtrs', response_class=HTMLResponse, response_model=List[ProductSchema])
async def product_filtr(request: Request, brand: str = Query(None), price: str = Query(None), 
                        select_item: str = Query(None), session: AsyncSession=Depends(get_session),  page: int = 1, 
                        current_user: dict = Depends(get_current_user)):

    if brand != None:
        brand = brand.split(',')
    if price != None:
        price = price.split('-')
    dictionary = {}
    limit = 12
    print({'brand': brand, 'price': price, 'select_item': select_item})

    for i in range(1, 100): 
        if i == 1:
            dictionary[i] = 0
        else:
            dictionary[i] = dictionary[i-1] + 12
    
    print({'page': page})
    products = await service.get_filter_prod(session, brand=brand, price=price, select_item=select_item, skip=dictionary[page], limit=limit)
    products_all = await service.get_filter_prod_all(session, brand=brand, price=price, select_item=select_item)
    data_brand = await service.get_brand_name(session)
    # print({'prod': len(products_all)})
    
    list_all = len(products_all) / 12
    return templates.TemplateResponse("shop.html", {"request": request, 'products': products, 
                                                    'brand': data_brand, 'product_all': int(list_all), 'products_all': products_all,
                                                    'dictionary': dictionary, 'page': page, 'current_user': current_user, 'price': price,
                                                    'bool_filtr': True, 'query': request.query_params})
    
@app.get('/shoes/{name_product}/{id_product}', response_class=HTMLResponse, response_model=List[ProductSchema])
async def product_page(name_product: str, id_product: int,  request: Request, session: AsyncSession=Depends(get_session), 
                       current_user: dict = Depends(get_current_user)):
    product = await service.get_product_page(session, id_product)
    products_all = await service.get_product_all(session)
    return templates.TemplateResponse("product-page.html", {"request": request, 'product': product, 
                                                            'name_product': name_product, 'current_user': current_user, 
                                                            'products_all': products_all})

@app.get('/login', response_class=HTMLResponse)
async def login(request: Request, session: AsyncSession=Depends(get_session), current_user: dict = Depends(get_current_user)):
    if not current_user:
        return templates.TemplateResponse('login.html', {'request': request})
    return RedirectResponse(url="/")

@app.get('/register', response_class=HTMLResponse)
async def register(request: Request, session: AsyncSession=Depends(get_session), current_user: dict = Depends(get_current_user)):
    if not current_user:
        return templates.TemplateResponse('register.html', {'request': request})
    return RedirectResponse(url="/")

@app.post('/register', response_model=UserSchema)
async def register_token(user: UserSchema, session: AsyncSession=Depends(get_session)):
    token = secrets.token_hex(16)
    hashed_password = await hash_password(user.password)
    data = {
        'password': hashed_password,
        'activate': token
    }
    user.add_data(data)        #добавляем в модель пользователя захэшированный пароль и токен для активации учетной записи
    add_user = await service.register_user(session, name=user.name, phone=user.phone, email=user.email, 
                                        password=user.password, subscribe=user.subscribe, 
                                        token=user.activate)
    await session.commit()
    print(token)    #<-------НУЖНО ДОПИСАТЬ ФУНКЦИЮ ДЛЯ ОТПРАВКИ ПОЛЬЗОВАТЕЛЮ НА ПОЧТУ ТОКЕН ДЛЯ ПОДТВЕРЖДЕНИЯ
    return user

@app.get('/register/{activate}')
async def finish_register(activate: str,  session: AsyncSession=Depends(get_session)):
    user = await service.get_user(session, activate)
    try:
        user = user[0][0]
        if user.activate == activate:   #сверяем ключ активации
            user = await service.activate_user(session, activate)
            await session.commit()
            return 'Регистрация подтверждена'
        else:
            return 'Ошибка 404'
    except Exception:
        return 'Ошибка 404'

#аутентификация пользователя
@app.post('/login')
async def auth_login(response: Response, user: UserAuth, session: AsyncSession=Depends(get_session) ):
    user_sql = await service.get_user_login(session, user.email)    #получаем пользователя из бд для проверки данных 
    user_sql = user_sql[0]
    if user_sql.activate != 'activate':     #проверка подтвердил ли пользователь свой профиль
        return 'Не подтвержденный профиль!!!'
    is_password_correct = pwd_context.verify(user.password, user_sql.password)
    jwt_token = create_jwt_token({"sub": user_sql.email})
    response.set_cookie(key="jwt_token", value=jwt_token)   #сохраняем токен в куки сайта
    return {"access_token": jwt_token, "token_type": "bearer", 
            'user_id': user_sql.id, 'email': user_sql.email }
# Выход
@app.post('/logout')
async def logout(response: Response, current_user: dict = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/")
    response.delete_cookie("jwt_token")
    return {'del': 'del'}
# добавление в избранное товар
@app.post("/add/product/wishlist/")
async def add_product_wishlist(product_wish: ProductWish, current_user: dict = Depends(get_current_user),
                               session: AsyncSession=Depends(get_session)):
    user = current_user[0]
    wish = []
    if user.product_list == None:
        wish.append(int(product_wish.id_product))
        await service.add_wish(session, user.email, wish)
        await session.commit()
        return wish
    for i in user.product_list:
        if i == int(product_wish.id_product):
            return None
    info_product = await service.get_product_page(session, int(product_wish.id_product))
    user.product_list.append(int(product_wish.id_product))
    await service.add_wish(session, user.email, user.product_list)
    await session.commit()
    return {'product_list': user.product_list, 'info_product': info_product}
# удаление из избранного
@app.post("/delete/product/wishlist/")
async def delete_product_wishlist(product_wish: ProductWish, current_user: dict = Depends(get_current_user),
                               session: AsyncSession=Depends(get_session)):
    user = current_user[0]
    user.product_list.remove(int(product_wish.id_product))
    await service.add_wish(session, user.email, user.product_list)
    await session.commit()
    return user.product_list

@app.get('/wishlist', response_class=HTMLResponse)
async def login(request: Request, session: AsyncSession=Depends(get_session), 
                current_user: dict = Depends(get_current_user)):
    products_all = await service.get_product_all(session)
    return templates.TemplateResponse('wishlist.html', {'request': request, 
                                                        'current_user': current_user,
                                                        'products_all': products_all})

@app.post("/add/sub/")
async def subscribe(current_user: dict = Depends(get_current_user),
                    session: AsyncSession=Depends(get_session)):
    
    user = current_user[0]
    await service.subscribe_me_up(session, user.email)
    await session.commit()
    return 123