from src.domain.entities import InvalidOperation, Location, Movement, ProductNotFound
from src.domain.ports import InventoryRepository, ProductRepository


class InventoryService:
    """Entradas a caja, traslados caja a cajón y salidas desde cajón."""

    def __init__(self, products: ProductRepository, inventory: InventoryRepository):
        self._products = products
        self._inventory = inventory

    def _find(self, codigo_qr: str):
        p = self._products.get_by_code(codigo_qr)
        if p is None:
            raise ProductNotFound(f"Product {codigo_qr} not found")
        return p

    @staticmethod
    def _check(cantidad: int) -> None:
        if cantidad <= 0:
            raise InvalidOperation("Quantity must be greater than zero")

    def register_entry(self, codigo_qr: str, cantidad: int, caja: str, usuario_id: int | None = None) -> Movement:
        self._check(cantidad)
        return self._inventory.apply_entry(self._find(codigo_qr).id, caja, cantidad, usuario_id)

    def register_exit(self, codigo_qr: str, cantidad: int, cajon: str, usuario_id: int | None = None) -> Movement:
        self._check(cantidad)
        return self._inventory.apply_exit(self._find(codigo_qr).id, cajon, cantidad, usuario_id)

    def transfer(self, codigo_qr: str, cantidad: int, caja: str, cajon: str,
                 usuario_id: int | None = None) -> Movement:
        self._check(cantidad)
        return self._inventory.apply_transfer(self._find(codigo_qr).id, caja, cajon, cantidad, usuario_id)

    def stock(self, codigo_qr: str) -> dict:
        p = self._find(codigo_qr)
        caja, cajon = self._inventory.totals(p.id)
        return {"codigo_qr": p.codigo_qr, "nombre": p.nombre, "caja": caja, "cajon": cajon,
                "total": caja + cajon, "minimo": p.stock_minimo_cajon}

    def snapshot(self) -> list[dict]:
        return self._inventory.snapshot()

    def movements(self, limit: int = 50, codigo_qr: str | None = None) -> list[dict]:
        pid = self._find(codigo_qr).id if codigo_qr else None
        return self._inventory.movements(limit, pid)

    def cajas(self) -> list[Location]:
        return self._inventory.list_cajas()

    def cajones(self) -> list[Location]:
        return self._inventory.list_cajones()

    def add_caja(self, codigo: str, descripcion: str = "") -> Location:
        return self._inventory.add_caja(codigo, descripcion)

    def add_cajon(self, codigo: str, capacidad: int | None = None, cantidad_minima: int = 0) -> Location:
        return self._inventory.add_cajon(codigo, capacidad, cantidad_minima)