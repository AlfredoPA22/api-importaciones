from typing import Optional
from pydantic import BaseModel, EmailStr

class Client(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    company: Optional[str] = None
    notes: Optional[str] = None

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    company: Optional[str] = None
    notes: Optional[str] = None

