from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Stock
from .schemas import StockCreate, StockUpdate


def list_stock(db: Session, skip: int = 0, limit: int = 100) -> list[Stock]:
    stmt = select(Stock).offset(skip).limit(limit).order_by(Stock.id)
    return list(db.scalars(stmt).all())


def get_stock_by_name(db: Session, stock_name: str) -> Stock | None:
    stmt = select(Stock).where(Stock.descripcion.ilike(f"%{stock_name}%"))
    return list(db.scalars(stmt).all())


def get_stock(db: Session, stock_id: int) -> Stock | None:
    return db.get(Stock, stock_id)


def create_stock(db: Session, data: StockCreate) -> Stock:
    item = Stock(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_stock(db: Session, item: Stock, data: StockUpdate) -> Stock:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


def delete_stock(db: Session, item: Stock) -> None:
    db.delete(item)
    db.commit()
