import os
from functools import lru_cache
from src.application.product_service import ProductService
from src.application.inventory_service import InventoryService
from src.application.replenishment_service import ReplenishmentService
from src.infrastructure.sql_repositories import SqlProductRepository, SqlMovementRepository
from src.infrastructure.colombia_open_data import OpenDataClient

@lru_cache
def _products(): return SqlProductRepository()
@lru_cache
def _movements(): return SqlMovementRepository()
@lru_cache
def _open_data(): return OpenDataClient()  # singleton: el circuit breaker conserva su estado

def get_product_service(): return ProductService(_products())
def get_inventory_service(): return InventoryService(_products(), _movements())
def get_open_data(): return _open_data()

def get_replenishment_service():
    advisor = None
    if os.getenv("GEMINI_API_KEY"):
        from src.infrastructure.gemini_advisor import GeminiAdvisor
        advisor = GeminiAdvisor()
    return ReplenishmentService(_products(), _movements(), advisor)
