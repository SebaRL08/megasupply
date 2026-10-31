from datetime import datetime
from sqlalchemy import func, case
from src.db.database import SessionLocal
from src.db.models import Producto, Movimiento
from src.domain.entities import Product, Movement

def _to_domain(r: Producto) -> Product:
    return Product(r.codigo_qr, r.nombre, r.stock_minimo_cajon or 0, r.descripcion or "", r.id)

class SqlProductRepository:
    def add(self, p: Product) -> Product:
        with SessionLocal() as s:
            r = Producto(codigo_qr=p.codigo_qr, nombre=p.nombre,
                         descripcion=p.descripcion, stock_minimo_cajon=p.stock_minimo_cajon)
            s.add(r); s.commit(); s.refresh(r)
            return _to_domain(r)

    def get(self, product_id):
        with SessionLocal() as s:
            r = s.get(Producto, product_id)
            return _to_domain(r) if r else None

    def get_by_code(self, codigo_qr):
        with SessionLocal() as s:
            r = s.query(Producto).filter(Producto.codigo_qr == codigo_qr).first()
            return _to_domain(r) if r else None

    def list(self):
        with SessionLocal() as s:
            return [_to_domain(r) for r in s.query(Producto).all()]

    def update(self, product_id, **fields):
        with SessionLocal() as s:
            r = s.get(Producto, product_id)
            if r is None:
                return None
            for k, v in fields.items():
                setattr(r, k, v)
            s.commit(); s.refresh(r)
            return _to_domain(r)

    def delete(self, product_id):
        with SessionLocal() as s:
            r = s.get(Producto, product_id)
            if r is None:
                return False
            s.delete(r); s.commit()
            return True

class SqlMovementRepository:
    def add(self, m: Movement) -> Movement:
        with SessionLocal() as s:
            r = Movimiento(tipo=m.tipo, producto_id=m.product_id, cantidad=m.cantidad,
                           origen=m.origen, destino=m.destino,
                           fecha_hora=m.fecha_hora or datetime.now())
            s.add(r); s.commit(); s.refresh(r)
            m.id = r.id
            return m

    def stock_of(self, product_id: int) -> int:
        with SessionLocal() as s:
            delta = case((Movimiento.tipo == "entrada", Movimiento.cantidad),
                         (Movimiento.tipo == "salida", -Movimiento.cantidad), else_=0)
            total = s.query(func.coalesce(func.sum(delta), 0)).filter(
                Movimiento.producto_id == product_id).scalar()
            return int(total)

        