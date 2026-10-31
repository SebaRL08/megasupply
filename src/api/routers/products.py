from dataclasses import asdict
from fastapi import APIRouter, Depends, status
from src.api.schemas.producto import ProductoCreate, ProductoResponse
from src.api.dependencies import get_product_service
from src.application.product_service import ProductService

router = APIRouter(prefix="/api/products", tags=["Products Management"])

@router.post("/", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
def create_product(body: ProductoCreate, svc: ProductService = Depends(get_product_service)):
    return asdict(svc.create(body.codigo_qr, body.nombre, body.descripcion or "", body.stock_minimo_cajon))

@router.get("/", response_model=list[ProductoResponse])
def list_products(svc: ProductService = Depends(get_product_service)):
    return [asdict(p) for p in svc.list()]

@router.get("/{product_id}", response_model=ProductoResponse)
def get_product(product_id: int, svc: ProductService = Depends(get_product_service)):
    return asdict(svc.get(product_id))

@router.put("/{product_id}", response_model=ProductoResponse)
def update_product(product_id: int, body: ProductoCreate, svc: ProductService = Depends(get_product_service)):
    return asdict(svc.update(product_id, **body.model_dump()))

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, svc: ProductService = Depends(get_product_service)):
    svc.delete(product_id)