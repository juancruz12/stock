from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from . import crud
from .database import Base, engine, get_db
from .schemas import StockCreate, StockOut, StockUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crea la tabla `stock` si no existe al iniciar.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Stock API",
    version="1.0.0",
    description="API básica de stock con FastAPI y PostgreSQL.",
    lifespan=lifespan,
)


@app.get("/", tags=["health"])
def root():
    return {"service": "stock-api", "status": "ok"}


@app.get("/health", tags=["health"])
def health(db: Session = Depends(get_db)):
    """Healthcheck que verifica la conexión a la base de datos."""
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="database unavailable",
        ) from exc
    return {"status": "healthy"}


@app.get("/stock", response_model=list[StockOut], tags=["stock"])
def list_stock(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_stock(db, skip=skip, limit=limit)


@app.get("/stock/{stock_id}", response_model=StockOut, tags=["stock"])
def get_stock(stock_id: int, db: Session = Depends(get_db)):
    item = crud.get_stock(db, stock_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="stock no encontrado")
    return item


@app.get("/stockByName/{stock_name}", response_model=list[StockOut], tags=["stock"])
def list_stock_by_name(stock_name: str, db: Session = Depends(get_db)):
    return crud.get_stock_by_name(db, stock_name)


@app.post("/stock", response_model=StockOut, status_code=status.HTTP_201_CREATED, tags=["stock"])
def create_stock(payload: StockCreate, db: Session = Depends(get_db)):
    return crud.create_stock(db, payload)


@app.put("/stock/{stock_id}", response_model=StockOut, tags=["stock"])
def update_stock(stock_id: int, payload: StockUpdate, db: Session = Depends(get_db)):
    item = crud.get_stock(db, stock_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="stock no encontrado")
    return crud.update_stock(db, item, payload)


@app.delete("/stock/{stock_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["stock"])
def delete_stock(stock_id: int, db: Session = Depends(get_db)):
    item = crud.get_stock(db, stock_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="stock no encontrado")
    crud.delete_stock(db, item)
