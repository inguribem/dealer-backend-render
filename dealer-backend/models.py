from pydantic import BaseModel
from typing import Optional

class Vehicle(BaseModel):
    vin: str
    year: Optional[int]
    make: Optional[str]
    model: Optional[str]
    trim: Optional[str] = ""
    price_purchase: Optional[float] = None
    miles: Optional[int] = None
    dealer_name: Optional[str] = ""
    city: Optional[str] = ""
    state: Optional[str] = ""
    status: Optional[str] = "new"
