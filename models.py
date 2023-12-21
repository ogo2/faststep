import sqlalchemy as db
import psycopg2
from sqlalchemy import create_engine, MetaData, Table, Integer, String, ARRAY, Float, Column, DateTime, ForeignKey, Numeric, SmallInteger, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import insert
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from config import DB_CONNECT

Base = declarative_base()

class User(Base):
    __tablename__='users'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    phone = Column(String(18), nullable=False)
    email = Column(String(120), nullable=False)
    password = Column(String(220), nullable=False)
    product_list = Column(ARRAY(Integer), nullable=True)
    date_registr = Column(DateTime(), nullable=False, default=datetime.utcnow)

class Product(Base):
    __tablename__='products'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(220), nullable=False)
    photo_path = Column(String(300), nullable=False)
    price = Column(Integer(), nullable=False)
    old_price = Column(Integer(), nullable=False)
    url_product = Column(String(120), nullable=False)
    stars = Column(ARRAY(Integer), nullable=True)
    date = Column(DateTime(), nullable=False, default=datetime.utcnow)
    sex = Column(String(20), nullable=False)
    brand = Column(String(120), nullable=False)
    
class History(Base):
    __tablename__ = 'history'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    name_brand = Column(String(120), nullable=False)
    text_history = Column(Text(), nullable=False)

# Base.metadata.create_all(engine)