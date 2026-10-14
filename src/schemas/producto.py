"""
Module: producto.py
Description: Pydantic schemas for data validation and serialization of inventory products in MegaSupply.
Author: Sebastián Restrepo - Santiago Rocha (MegaSupply Team)
"""

from pydantic import BaseModel, Field
from typing import Optional

class ProductoCreate(BaseModel):
    """
    Schema representing the required payload to create or update a product.
    Includes data validation rules to automatically trigger HTTP 400/422 on bad requests.
    """
    codigo_qr: str = Field(..., description="Unique QR code identifier for the product (e.g., PROD-001)")
    nombre: str = Field(..., min_length=1, description="Commercial name of the product")
    descripcion: Optional[str] = Field(None, description="Detailed description of the product and its characteristics")
    stock_minimo_cajon: int = Field(..., ge=0, description="Minimum allowable stock limit in the drawer (must be >= 0)")

class ProductoResponse(ProductoCreate):
    """
    Schema representing the product returned to the client, including the database assigned ID.
    """
    id: int = Field(..., description="Unique database primary key identifier")

    class Config:
        from_attributes = True