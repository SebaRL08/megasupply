from dataclasses import dataclass
from datetime import datetime

@dataclass
class Product:
    codigo_qr: str
    nombre: str
    stock_minimo_cajon: int = 0
    descripcion: str = ""
    id: int | None = None

@dataclass
class Movement:
    tipo: str  # entrada | salida | traslado
    product_id: int
    cantidad: int
    origen: str | None = None
    destino: str | None = None
    fecha_hora: datetime | None = None
    id: int | None = None

class ProductNotFound(Exception): ...
class DuplicateProduct(Exception): ...
class InsufficientStock(Exception): ...
