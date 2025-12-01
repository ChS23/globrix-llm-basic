from pydantic import BaseModel
from typing import Optional

class ApartmentSearchFilter(BaseModel):
    apartment_type: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None