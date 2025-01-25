from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional, List, Dict, Any

from db_conf import Base


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    artikul = Column(String, unique=True, index=True)
    name = Column(String)
    price = Column(Float)
    rating = Column(Float)
    total_quantity = Column(Integer)
    last_update = Column(DateTime, default=datetime.utcnow)
    is_update = Column(Boolean, default=False)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    tg_id = Column(String)
    jwt_token = Column(String)
    is_active = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User(id={self.id}, tg_id={self.tg_id}, is_active={self.is_active}, is_admin={self.is_admin}, created_at={self.created_at})>"

    def __str__(self):
        return f"{self.id}, {self.tg_id}, {self.jwt_token}, {self.is_active}, {self.is_admin}, {self.created_at}"
