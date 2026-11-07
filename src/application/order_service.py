from datetime import date

from src.domain.entities import InvalidOperation, Order, OrderNotFound, ProductNotFound
from src.domain.ports import OrderRepository, ProductRepository

STATES = {"pendiente", "completado"}


class OrderService:
    """Pedidos próximos de producto, usados como insumo del abastecimiento."""

    def __init__(self, products: ProductRepository, orders: OrderRepository):
        self._products = products
        self._orders = orders

    def create(self, codigo_qr: str, cantidad: int, fecha_esperada: date | None) -> Order:
        if cantidad <= 0:
            raise InvalidOperation("Quantity must be greater than zero")
        p = self._products.get_by_code(codigo_qr)
        if p is None:
            raise ProductNotFound(f"Product {codigo_qr} not found")
        return self._orders.add(Order(p.id, cantidad, fecha_esperada))

    def list(self, estado: str | None = None) -> list[Order]:
        return self._orders.list(estado)

    def set_state(self, order_id: int, estado: str) -> Order:
        if estado not in STATES:
            raise InvalidOperation(f"State must be one of {sorted(STATES)}")
        o = self._orders.set_state(order_id, estado)
        if o is None:
            raise OrderNotFound(f"Order {order_id} not found")
        return o