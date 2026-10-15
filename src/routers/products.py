from fastapi import APIRouter, HTTPException, status, Query
from typing import List
from pydantic import BaseModel, Field

# Definimos el router con su prefijo y etiqueta para Swagger
router = APIRouter(prefix="/api/products", tags=["Products Management"])

class ProductBase(BaseModel):
    name: str = Field(..., description="Product name in MegaSupply inventory")
    stock: int = Field(..., ge=0, description="Current stock quantity")
    min_threshold: int = Field(..., ge=0, description="Minimum drawer requirement threshold")

class ProductResponse(ProductBase):
    id: int

# Base de datos simulada en memoria (puedes reemplazarla con SQLAlchemy después)
fake_db = []

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED, summary="Create a new inventory product")
def create_product(product: ProductBase):
    """Create a new product with strict validation rules."""
    new_id = len(fake_db) + 1
    new_product = {"id": new_id, **product.dict()}
    fake_db.append(new_product)
    return new_product

@router.get("/", response_model=List[ProductResponse], summary="List all products with pagination")
def get_products(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100)):
    """Retrieve paginated products list."""
    return fake_db[skip : skip + limit]

@router.get("/{product_id}", response_model=ProductResponse, summary="Get product by ID")
def get_product(product_id: int):
    """Fetch product by ID with 404 error handling."""
    product = next((p for p in fake_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} was not found in MegaSupply inventory."
        )
    return product

@router.put("/{product_id}", response_model=ProductResponse, summary="Update an existing product")
def update_product(product_id: int, updated_data: ProductBase):
    """Update product details."""
    product = next((p for p in fake_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found for update."
        )
    product.update(updated_data.dict())
    return product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a product")
def delete_product(product_id: int):
    """Delete product by ID."""
    global fake_db
    product = next((p for p in fake_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found for deletion."
        )
    fake_db = [p for p in fake_db if p["id"] != product_id]
    return None