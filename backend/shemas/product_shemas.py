import pytz
from pydantic import BaseModel, Field
from datetime import datetime


class ArticularResponse(BaseModel):
    artikul: str


class ProductCreate(BaseModel):
    artikul: str = Field(..., description="Артикул товара")
    name: str = Field(..., description="Название товара")
    price: float = Field(..., description="Цена товара")
    rating: float = Field(..., description="Рейтинг товара")
    total_quantity: int = Field(..., description="Общее количество на складах")

class ProductResponse(ProductCreate):
    artikul: str
    name: str
    price: float
    rating: float
    total_quantity: int
    last_update: datetime = Field(default_factory=lambda: datetime.now(pytz.timezone("Europe/Moscow")))

    class Config:
        from_attributes = True