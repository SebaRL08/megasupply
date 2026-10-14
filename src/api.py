"""
Module: api.py
Description: Main FastAPI application for MegaSupply. Implements pre-class REST endpoints 
             for inventory management with OpenAPI 3.0 documentation.
Author: Santiago - Sebastián (MegaSupply Team)
"""

from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Generator

from src.db.database import SessionLocal
from src.db.models import Producto
from src.schemas.producto import ProductoCreate, ProductoResponse

# Initialize FastAPI application with metadata for OpenAPI 3.0
app = FastAPI(
    title="MegaSupply API - Session 9 Pre-class Task",
    description="REST API for inventory management in MegaSupply, featuring CRUD operations and OpenAPI documentation.",
    version="1.0.0"
)

def get_db() -> Generator[Session, None, None]:
    """
    Dependency generator to obtain a SQLAlchemy database session per request.
    Ensures the session is safely closed after execution.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------
# ENDPOINT 1: GET - List products with pagination (HTTP 200)
# ---------------------------------------------------------
@app.get(
    "/api/v1/productos",
    response_model=List[ProductoResponse],
    summary="Get all products with pagination",
    description="Retrieves a paginated list of products registered in the database. Returns HTTP 200 OK."
)
def listar_productos(
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Fetches a subset of products from the database using offset-based pagination.
    """
    productos = db.query(Producto).offset(skip).limit(limit).all()
    return productos


# ---------------------------------------------------------
# ENDPOINT 2: GET by ID - Find product (HTTP 200 or 404)
# ---------------------------------------------------------
@app.get(
    "/api/v1/productos/{id}",
    response_model=ProductoResponse,
    summary="Get product by ID",
    description="Retrieves a single product by its unique database ID. Returns HTTP 200 OK or HTTP 404 Not Found."
)
def obtener_producto_por_id(id: int, db: Session = Depends(get_db)):
    """
    Queries a specific product by its primary key ID.
    """
    producto = db.query(Producto).filter(Producto.id == id).first()
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {id} not found"
        )
    return producto


# ---------------------------------------------------------
# ENDPOINT 3: POST - Create product (HTTP 201 or 400/422)
# ---------------------------------------------------------
@app.post(
    "/api/v1/productos",
    response_model=ProductoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
    description="Creates a new inventory product with validation rules. Returns HTTP 201 Created or HTTP 400 Bad Request."
)
def crear_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    """
    Creates a new product record in the PostgreSQL database after validating the payload.
    """
    nuevo_producto = Producto(
        codigo_qr=producto.codigo_qr,
        nombre=producto.nombre,
        descripcion=producto.descripcion,
        stock_minimo_cajon=producto.stock_minimo_cajon
    )
    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto)
    return nuevo_producto