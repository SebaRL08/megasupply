"""Entidades y errores del dominio. No dependen de ninguna herramienta externa."""
from dataclasses import dataclass
from datetime import date, datetime


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
    usuario_id: int | None = None
    id: int | None = None


@dataclass
class Location:
    id: int
    codigo: str
    descripcion: str = ""


@dataclass
class Order:
    product_id: int
    cantidad_solicitada: int
    fecha_esperada: date | None = None
    estado: str = "pendiente"
    codigo_qr: str = ""
    id: int | None = None


@dataclass
class Recommendation:
    product_id: int
    fecha_hora: datetime
    stock_actual: int
    demanda_estimada: int
    pedidos_pendientes: int
    cantidad_sugerida: int
    nivel_riesgo: str
    datos_base: str
    estado: str = "pendiente"
    cantidad_final: int | None = None
    codigo_qr: str = ""
    nombre: str = ""
    id: int | None = None


class ProductNotFound(Exception): ...
class DuplicateProduct(Exception): ...
class ProductInUse(Exception): ...
class InsufficientStock(Exception): ...
class LocationNotFound(Exception): ...
class InvalidOperation(Exception): ...
class OrderNotFound(Exception): ...
class RecommendationNotFound(Exception): ...