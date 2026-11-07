from src.domain.entities import ProductNotFound
from src.domain.ports import AIAdvisor, InventoryRepository, OrderRepository, ProductRepository


class ReplenishmentService:
    """Alertas de reabastecimiento por regla de negocio; la IA solo opina si se le pide."""

    def __init__(self, products: ProductRepository, inventory: InventoryRepository,
                 orders: OrderRepository, advisor: AIAdvisor | None = None):
        self._products = products
        self._inventory = inventory
        self._orders = orders
        self._advisor = advisor

    def assess(self, codigo_qr: str, use_ai: bool = False) -> dict:
        p = self._products.get_by_code(codigo_qr)
        if p is None:
            raise ProductNotFound(f"Product {codigo_qr} not found")
        caja, cajon = self._inventory.totals(p.id)
        result = {"codigo_qr": codigo_qr, "caja": caja, "cajon": cajon, "minimo": p.stock_minimo_cajon,
                  "pedidos_pendientes": self._orders.pending_quantity(p.id),
                  "reorder_suggested": cajon < p.stock_minimo_cajon}
        if use_ai and self._advisor:
            try:
                result["ai"] = self._advisor.advise(
                    f"Product {p.nombre}: {caja} in boxes, {cajon} in drawers, drawer minimum "
                    f"{p.stock_minimo_cajon}. Keys: reorder_suggested, reasoning.")
            except Exception as exc:  # la IA es opcional: nunca debe romper el flujo
                result["ai_error"] = str(exc)
        return result

    def alerts(self) -> list[dict]:
        out = []
        for p in self._products.list():
            caja, cajon = self._inventory.totals(p.id)
            if cajon < p.stock_minimo_cajon:
                out.append({
                    "codigo_qr": p.codigo_qr, "nombre": p.nombre, "cajon": cajon,
                    "minimo": p.stock_minimo_cajon, "caja": caja,
                    "faltante": p.stock_minimo_cajon - cajon,
                    "accion": "Trasladar desde cajas" if caja > 0 else "Sin stock en cajas: pedir mercancía",
                    "estado": "REQUIERE REABASTECIMIENTO"})
        return sorted(out, key=lambda a: a["faltante"], reverse=True)