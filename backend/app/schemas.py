from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class StockBase(BaseModel):
    descripcion: str = Field(..., min_length=1, max_length=255)
    cantidad: int = Field(..., ge=0)
    precio: Decimal = Field(..., ge=0, max_digits=12, decimal_places=2)


class StockCreate(StockBase):
    pass


class StockUpdate(BaseModel):
    descripcion: str | None = Field(None, min_length=1, max_length=255)
    cantidad: int | None = Field(None, ge=0)
    precio: Decimal | None = Field(None, ge=0, max_digits=12, decimal_places=2)


class StockOut(StockBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
