"""Adaptadores SQL (PostgreSQL en producción, SQLite en pruebas)."""
from datetime import date, datetime

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from src.db.database import SessionLocal
from src.db.models import (Caja, CajaProducto, Cajon, CajonProducto, Movimiento, Pedido,
                           Producto, Recomendacion)
from src.domain.entities import (InsufficientStock, InvalidOperation, Location, LocationNotFound,
                                 Movement, Order, Product, ProductInUse, Recommendation)


def _product(r: Producto) -> Product:
    return Product(r.codigo_qr, r.nombre, r.stock_minimo_cajon or 0, r.descripcion or "", r.id)


class SqlProductRepository:
    def __init__(self, session_factory=None):
        self._sf = session_factory or SessionLocal

    def add(self, p: Product) -> Product:
        with self._sf() as s:
            r = Producto(codigo_qr=p.codigo_qr, nombre=p.nombre, descripcion=p.descripcion,
                         stock_minimo_cajon=p.stock_minimo_cajon)
            s.add(r)
            s.commit()
            s.refresh(r)
            return _product(r)

    def get(self, product_id):
        with self._sf() as s:
            r = s.get(Producto, product_id)
            return _product(r) if r else None

    def get_by_code(self, codigo_qr):
        with self._sf() as s:
            r = s.query(Producto).filter(Producto.codigo_qr == codigo_qr).first()
            return _product(r) if r else None

    def list(self):
        with self._sf() as s:
            return [_product(r) for r in s.query(Producto).order_by(Producto.codigo_qr).all()]

    def update(self, product_id, **fields):
        with self._sf() as s:
            r = s.get(Producto, product_id)
            if r is None:
                return None
            for k, v in fields.items():
                setattr(r, k, v)
            s.commit()
            s.refresh(r)
            return _product(r)

    def delete(self, product_id):
        with self._sf() as s:
            r = s.get(Producto, product_id)
            if r is None:
                return False
            try:
                s.delete(r)
                s.commit()
            except IntegrityError as exc:
                s.rollback()
                raise ProductInUse("Product has stock, movements or orders and cannot be deleted") from exc
            return True


def _total(s, model, product_id) -> int:
    return int(s.query(func.coalesce(func.sum(model.cantidad), 0)).filter(model.producto_id == product_id).scalar())


class SqlInventoryRepository:
    def __init__(self, session_factory=None):
        self._sf = session_factory or SessionLocal

    # ---- ubicaciones
    def list_cajas(self):
        with self._sf() as s:
            return [Location(r.id, r.codigo_ubicacion, r.descripcion or "")
                    for r in s.query(Caja).order_by(Caja.codigo_ubicacion).all()]

    def list_cajones(self):
        with self._sf() as s:
            return [Location(r.id, r.codigo_ubicacion, "") for r in s.query(Cajon).order_by(Cajon.codigo_ubicacion).all()]

    def _create(self, row, codigo, descripcion=""):
        with self._sf() as s:
            s.add(row)
            try:
                s.commit()
            except IntegrityError as exc:
                s.rollback()
                raise InvalidOperation(f"Location {codigo} already exists or has invalid values") from exc
            s.refresh(row)
            return Location(row.id, row.codigo_ubicacion, descripcion)

    def add_caja(self, codigo, descripcion=""):
        return self._create(Caja(codigo_ubicacion=codigo, descripcion=descripcion), codigo, descripcion)

    def add_cajon(self, codigo, capacidad=None, cantidad_minima=0):
        return self._create(Cajon(codigo_ubicacion=codigo, capacidad=capacidad, cantidad_minima=cantidad_minima), codigo)

    @staticmethod
    def _caja(s, codigo):
        r = s.query(Caja).filter(Caja.codigo_ubicacion == codigo).first()
        if r is None:
            raise LocationNotFound(f"Box {codigo} not found")
        return r

    @staticmethod
    def _cajon(s, codigo):
        r = s.query(Cajon).filter(Cajon.codigo_ubicacion == codigo).first()
        if r is None:
            raise LocationNotFound(f"Drawer {codigo} not found")
        return r

    @staticmethod
    def _change(s, model, loc_col, loc_id, product_id, delta):
        row = s.get(model, (loc_id, product_id))
        current = row.cantidad if row else 0
        if current + delta < 0:
            raise InsufficientStock(f"Only {current} units available in that location")
        if row is None:
            s.add(model(**{loc_col: loc_id, "producto_id": product_id, "cantidad": delta}))
        else:
            row.cantidad = current + delta

    @staticmethod
    def _log(s, tipo, product_id, cantidad, origen, destino, usuario_id) -> Movement:
        mov = Movimiento(tipo=tipo, producto_id=product_id, cantidad=cantidad, origen=origen,
                         destino=destino, fecha_hora=datetime.now(), usuario_id=usuario_id)
        s.add(mov)
        s.flush()
        return Movement(tipo, product_id, cantidad, origen, destino, mov.fecha_hora, usuario_id, mov.id)

    # ---- operaciones atómicas
    def apply_entry(self, product_id, caja, cantidad, usuario_id=None):
        with self._sf() as s:
            c = self._caja(s, caja)
            self._change(s, CajaProducto, "caja_id", c.id, product_id, cantidad)
            mov = self._log(s, "entrada", product_id, cantidad, None, c.codigo_ubicacion, usuario_id)
            s.commit()
            return mov

    def apply_exit(self, product_id, cajon, cantidad, usuario_id=None):
        with self._sf() as s:
            d = self._cajon(s, cajon)
            self._change(s, CajonProducto, "cajon_id", d.id, product_id, -cantidad)
            mov = self._log(s, "salida", product_id, cantidad, d.codigo_ubicacion, None, usuario_id)
            s.commit()
            return mov

    def apply_transfer(self, product_id, caja, cajon, cantidad, usuario_id=None):
        with self._sf() as s:
            c, d = self._caja(s, caja), self._cajon(s, cajon)
            self._change(s, CajaProducto, "caja_id", c.id, product_id, -cantidad)
            if d.capacidad is not None:
                used = int(s.query(func.coalesce(func.sum(CajonProducto.cantidad), 0))
                           .filter(CajonProducto.cajon_id == d.id).scalar())
                if used + cantidad > d.capacidad:
                    raise InvalidOperation(f"Drawer {d.codigo_ubicacion} capacity exceeded ({used}/{d.capacidad})")
            self._change(s, CajonProducto, "cajon_id", d.id, product_id, cantidad)
            mov = self._log(s, "traslado", product_id, cantidad, c.codigo_ubicacion, d.codigo_ubicacion, usuario_id)
            s.commit()
            return mov

    # ---- consultas
    def totals(self, product_id):
        with self._sf() as s:
            return _total(s, CajaProducto, product_id), _total(s, CajonProducto, product_id)

    def snapshot(self):
        with self._sf() as s:
            rows = []
            for p in s.query(Producto).order_by(Producto.codigo_qr).all():
                caja, cajon = _total(s, CajaProducto, p.id), _total(s, CajonProducto, p.id)
                places = [f"{c}: {q}" for c, q in s.query(Caja.codigo_ubicacion, CajaProducto.cantidad)
                          .join(CajaProducto, CajaProducto.caja_id == Caja.id)
                          .filter(CajaProducto.producto_id == p.id, CajaProducto.cantidad > 0).all()]
                places += [f"{c}: {q}" for c, q in s.query(Cajon.codigo_ubicacion, CajonProducto.cantidad)
                           .join(CajonProducto, CajonProducto.cajon_id == Cajon.id)
                           .filter(CajonProducto.producto_id == p.id, CajonProducto.cantidad > 0).all()]
                rows.append({"codigo_qr": p.codigo_qr, "nombre": p.nombre, "caja": caja, "cajon": cajon,
                             "total": caja + cajon, "minimo": p.stock_minimo_cajon,
                             "ubicaciones": ", ".join(places)})
            return rows

    def movements(self, limit=50, product_id=None):
        with self._sf() as s:
            q = s.query(Movimiento, Producto.codigo_qr, Producto.nombre).join(
                Producto, Producto.id == Movimiento.producto_id)
            if product_id is not None:
                q = q.filter(Movimiento.producto_id == product_id)
            rows = q.order_by(Movimiento.fecha_hora.desc(), Movimiento.id.desc()).limit(limit).all()
            return [{"id": m.id, "fecha_hora": m.fecha_hora, "tipo": m.tipo, "codigo_qr": c, "nombre": n,
                     "cantidad": m.cantidad, "origen": m.origen, "destino": m.destino,
                     "es_simulado": m.es_simulado} for m, c, n in rows]

    def daily_outflows(self, product_id, since):
        with self._sf() as s:
            day = func.date(Movimiento.fecha_hora)
            rows = (s.query(day, func.sum(Movimiento.cantidad))
                    .filter(Movimiento.tipo == "salida", Movimiento.producto_id == product_id,
                            Movimiento.fecha_hora >= since)
                    .group_by(day).order_by(day).all())
            return [(date.fromisoformat(str(d)[:10]), int(q)) for d, q in rows]

    def has_simulated_data(self, product_id):
        with self._sf() as s:
            return s.query(Movimiento.id).filter(Movimiento.producto_id == product_id,
                                                 Movimiento.es_simulado.is_(True)).first() is not None

    def monthly_outflows(self, year, month):
        start = datetime(year, month, 1)
        end = datetime(year + (month == 12), month % 12 + 1, 1)
        with self._sf() as s:
            total = func.sum(Movimiento.cantidad)
            rows = (s.query(Producto.codigo_qr, Producto.nombre, total, func.count(Movimiento.id))
                    .join(Movimiento, Movimiento.producto_id == Producto.id)
                    .filter(Movimiento.tipo == "salida", Movimiento.fecha_hora >= start, Movimiento.fecha_hora < end)
                    .group_by(Producto.id, Producto.codigo_qr, Producto.nombre)
                    .order_by(total.desc()).all())
            return [{"codigo_qr": c, "nombre": n, "unidades": int(u), "salidas": int(k)} for c, n, u, k in rows]


def _order(r: Pedido, code: str) -> Order:
    return Order(r.producto_id, r.cantidad_solicitada, r.fecha_esperada, r.estado, code, r.id)


class SqlOrderRepository:
    def __init__(self, session_factory=None):
        self._sf = session_factory or SessionLocal

    def add(self, o: Order) -> Order:
        with self._sf() as s:
            r = Pedido(producto_id=o.product_id, cantidad_solicitada=o.cantidad_solicitada,
                       fecha_esperada=o.fecha_esperada, estado=o.estado)
            s.add(r)
            s.flush()
            out = _order(r, s.get(Producto, o.product_id).codigo_qr)
            s.commit()
            return out

    def list(self, estado=None):
        with self._sf() as s:
            q = s.query(Pedido, Producto.codigo_qr).join(Producto, Producto.id == Pedido.producto_id)
            if estado:
                q = q.filter(Pedido.estado == estado)
            return [_order(r, c) for r, c in q.order_by(Pedido.fecha_esperada, Pedido.id).all()]

    def set_state(self, order_id, estado):
        with self._sf() as s:
            r = s.get(Pedido, order_id)
            if r is None:
                return None
            r.estado = estado
            s.flush()
            out = _order(r, s.get(Producto, r.producto_id).codigo_qr)
            s.commit()
            return out

    def pending_quantity(self, product_id):
        with self._sf() as s:
            return int(s.query(func.coalesce(func.sum(Pedido.cantidad_solicitada), 0))
                       .filter(Pedido.producto_id == product_id, Pedido.estado == "pendiente").scalar())


def _rec(r: Recomendacion, p: Producto) -> Recommendation:
    return Recommendation(r.producto_id, r.fecha_hora, r.stock_actual, r.demanda_estimada,
                          r.pedidos_pendientes, r.cantidad_sugerida, r.nivel_riesgo, r.datos_base,
                          r.estado, r.cantidad_final, p.codigo_qr, p.nombre, r.id)


class SqlRecommendationRepository:
    def __init__(self, session_factory=None):
        self._sf = session_factory or SessionLocal

    def add(self, rec: Recommendation) -> Recommendation:
        with self._sf() as s:
            r = Recomendacion(producto_id=rec.product_id, fecha_hora=rec.fecha_hora, stock_actual=rec.stock_actual,
                              demanda_estimada=rec.demanda_estimada, pedidos_pendientes=rec.pedidos_pendientes,
                              cantidad_sugerida=rec.cantidad_sugerida, nivel_riesgo=rec.nivel_riesgo,
                              datos_base=rec.datos_base, estado=rec.estado)
            s.add(r)
            s.flush()
            out = _rec(r, s.get(Producto, r.producto_id))
            s.commit()
            return out

    def list(self, estado=None):
        with self._sf() as s:
            q = s.query(Recomendacion, Producto).join(Producto, Producto.id == Recomendacion.producto_id)
            if estado:
                q = q.filter(Recomendacion.estado == estado)
            return [_rec(r, p) for r, p in q.order_by(Recomendacion.fecha_hora.desc()).all()]

    def get(self, rec_id):
        with self._sf() as s:
            r = s.get(Recomendacion, rec_id)
            return _rec(r, s.get(Producto, r.producto_id)) if r else None

    def decide(self, rec_id, estado, cantidad_final):
        with self._sf() as s:
            r = s.get(Recomendacion, rec_id)
            if r is None:
                return None
            r.estado, r.cantidad_final = estado, cantidad_final
            s.flush()
            out = _rec(r, s.get(Producto, r.producto_id))
            s.commit()
            return out
        
