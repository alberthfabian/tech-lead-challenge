from pydantic import BaseModel, Field
from typing import Optional

class DatasetGenRequest(BaseModel):
    output_path: str = Field(default="/app/data/transactions.csv.gz", description="Path into of the dataset")
    rows: int = Field(default=100_000, ge=1)
    customers: int = Field(default=20_000, ge=1)
    days: int = Field(default=30, ge=1)
    min_amount: int = Field(default=5_000, ge=0)
    max_amount: int = Field(default=500_000, ge=1)
    gzip: bool = Field(default=True, description="If true, saves .gz")
    seed: Optional[int] = Field(default=None, description="Seed for reproducibility")

class DatasetGenResponse(BaseModel):
    output_path: str
    rows: int
    customers: int
    days: int
    gzip: bool
    size_bytes: int
