from src.domain.entities import Product, ProductNotFound, DuplicateProduct
from src.domain.ports import ProductRepository

class ProductService:
    def __init__(self, repo: ProductRepository):
        self._repo = repo


    def create(self, codigo_qr, nombre, descripcion="", stock_minimo=0) -> Product:
        if self._repo.get_by_code(codigo_qr):
            raise DuplicateProduct(f"Product {codigo_qr} already exists")
        return self._repo.add(Product(codigo_qr, nombre, stock_minimo, descripcion))

    def get(self, product_id: int) -> Product:
        p = self._repo.get(product_id)
        if p is None:
            raise ProductNotFound(f"Product {product_id} not found")
        return p

    def list(self) -> list[Product]:
        return self._repo.list()

    def update(self, product_id: int, **fields) -> Product:
        p = self._repo.update(product_id, **fields)
        if p is None:
            raise ProductNotFound(f"Product {product_id} not found")
        return p

    def delete(self, product_id: int) -> None:
        if not self._repo.delete(product_id):
            raise ProductNotFound(f"Product {product_id} not found")

    def get_by_code(self, codigo_qr: str) -> Product:
        p = self._repo.get_by_code(codigo_qr)
        if p is None:
            raise ProductNotFound(f"Product {codigo_qr} not found")
        return p