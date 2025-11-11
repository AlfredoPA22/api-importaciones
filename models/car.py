from typing import Optional
from pydantic import BaseModel, Field

class Car(BaseModel):
    model: str
    brand: str
    year: int
    sale_price: float
    color: Optional[str] = None
    vin: Optional[str] = None
    description: Optional[str] = None

class CarUpdate(BaseModel):
    model: Optional[str] = None
    brand: Optional[str] = None
    year: Optional[int] = None
    sale_price: Optional[float] = None
    color: Optional[str] = None
    vin: Optional[str] = None
    description: Optional[str] = None
