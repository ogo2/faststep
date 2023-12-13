from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from config import DB_CONNECT

# Инициализация асинхронного движка и модели
engine = create_async_engine(DB_CONNECT, echo=True)
Base = declarative_base()             
# Указание echo=True при инициализации движка позволит нам увидеть сгенерированные SQL-запросы в консоли.
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False      
) 
# ассинхронная функция для очисти и воссоздания таблицы бд
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
        
# Dependency
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session