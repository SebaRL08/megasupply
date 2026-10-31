from src.domain.entities import ProductNotFound
from src.domain.ports import ProductRepository, MovementRepository, AIAdvisor

class ReplenishmentService:
    def __init__(self, products: ProductRepository, movements: MovementRepository,
                 advisor: AIAdvisor | None = None):
        self._products = products
        self._movements = movements
        self._advisor = advisor

    def assess(self, codigo_qr: str, use_ai: bool = False) -> dict:
        p = self._products.get_by_code(codigo_qr)
        if p is None:
            raise ProductNotFound(f"Product {codigo_qr} not found")
        stock = self._movements.stock_of(p.id)
        result = {"codigo_qr": codigo_qr, "stock": stock,
                  "minimo": p.stock_minimo_cajon,
                  "reorder_suggested": stock <= p.stock_minimo_cajon}
        if use_ai and self._advisor:  # la IA solo apoya; la regla de negocio decide primero
            result["ai"] = self._advisor.advise(
                f"Product {p.nombre}: stock {stock}, minimum {p.stock_minimo_cajon}. "
                "Keys: reorder_suggested, reasoning.")
        return result
    