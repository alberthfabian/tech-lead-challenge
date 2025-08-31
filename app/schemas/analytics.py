from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator

class TopCustomersRequest(BaseModel):
    path: str = Field(default="/app/data/transactions.csv.gz")
    # Use ONE: days  ó  (start & end)
    days: Optional[int] = Field(default=7, ge=1)
    start: Optional[datetime] = None
    end: Optional[datetime] = None

    top_customers: int = Field(default=10, ge=1, le=1000)
    mode: str = Field(default="auto", pattern="^(auto|exact|stream)$")
    capacity: int = Field(default=200, ge=10, le=100000)

    @model_validator(mode="after")
    def _check_time(self):
        if self.days is None and (self.start is None or self.end is None):
            raise ValueError("Must send 'days' or both 'start' and 'end'.")
        return self

class TopCustomerItem(BaseModel):
    customer_id: str
    count: int

class TopCustomersResponse(BaseModel):
    start_timestamp: int
    end_timestamp: int
    top_customers: int
    mode: str
    results: List[TopCustomerItem]
