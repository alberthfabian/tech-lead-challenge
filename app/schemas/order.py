from enum import IntEnum
from pydantic import BaseModel, Field, conint, confloat
from typing import List

class Stratum(IntEnum):
    UNO=1; DOS=2; TRES=3; CUATRO=4; CINCO=5; SEIS=6

class OrderItem(BaseModel):
    sku: str = Field(..., min_length=1)
    price: conint(ge=0)  # COP
    quantity: conint(ge=1)

class OrderRequest(BaseModel):
    stratum: Stratum
    items: List[OrderItem]

class OrderResponse(BaseModel):
    subtotal: conint(ge=0)
    shipping: conint(ge=0)
    discount: conint(ge=0)
    total: conint(ge=0)
