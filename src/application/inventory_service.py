from datetime import datetime
from src.domain.entities import Movement, ProductNotFound, InsufficientStock
from src.domain.ports import ProductRepository, MovementRepository

class InventoryService:
    def __init__(self, products: ProductRepository, movements: MovementRepository):
        self._products = products
        self._movements = movements

    def _find(self, codigo_qr):
        p = self._products.get_by_code(codigo_qr)
        if p is None:
            raise ProductNotFound(f"Product {codigo_qr} not found")
        return p

    def register_entry(self, codigo_qr: str, cantidad: int, destino: str = "CAJA") -> Movement:
        p = self._find(codigo_qr)
        return self._movements.add(Movement("entrada", p.id, cantidad, destino=destino, fecha_hora=datetime.now()))

    def register_exit(self, codigo_qr: str, cantidad: int, origen: str = "CAJON") -> Movement:
        p = self._find(codigo_qr)
        if self._movements.stock_of(p.id) < cantidad:
            raise InsufficientStock("Not enough stock for this exit")
        return self._movements.add(Movement("salida", p.id, cantidad, origen=origen, fecha_hora=datetime.now()))

    def stock(self, codigo_qr: str) -> int:
        return self._movements.stock_of(self._find(codigo_qr).id)
    