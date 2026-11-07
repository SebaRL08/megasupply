from dataclasses import asdict

from src.application.replenishment_service import ReplenishmentService
from src.domain.ports import InventoryRepository, OrderRepository, RecommendationRepository


class ReportService:
    """Informe mensual: demanda, salidas, productos por agotarse, pedidos y recomendaciones."""

    def __init__(self, inventory: InventoryRepository, replenishment: ReplenishmentService,
                 orders: OrderRepository, recommendations: RecommendationRepository):
        self._inventory = inventory
        self._replenishment = replenishment
        self._orders = orders
        self._recs = recommendations

    def monthly(self, year: int, month: int) -> dict:
        outflows = self._inventory.monthly_outflows(year, month)
        return {
            "period": f"{year}-{month:02d}",
            "most_demanded": outflows[:5],
            "most_outflow_count": sorted(outflows, key=lambda r: r["salidas"], reverse=True)[:5],
            "near_depletion": self._replenishment.alerts(),
            "pending_orders": len(self._orders.list("pendiente")),
            "recommendations": [asdict(r) for r in self._recs.list("pendiente")],
        }
