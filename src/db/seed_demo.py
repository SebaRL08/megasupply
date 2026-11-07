"""Reinicia la base y carga DATOS DE PRUEBA SIMULADOS (es_simulado=True). Ejecutar: python -m src.db.seed_demo"""
import random
from datetime import date, datetime, timedelta

from src.db import models as m
from src.db.database import Base, SessionLocal, engine

DAYS = 120
# (codigo, nombre, descripcion, minimo en cajón, demanda base diaria, tendencia, caja, cajón, dejar bajo)
PRODUCTS = [
    ("PROD-001", "Tela Algodón", "Rollo de tela de algodón", 15, 6, 0.04, "A-01", "C-01", False),
    ("PROD-002", "Hilo Poliéster", "Cono de 500 m", 20, 10, 0.00, "A-01", "C-02", False),
    ("PROD-003", "Botones Metálicos", "Bolsa de 100 unidades", 25, 8, 0.08, "A-02", "C-03", True),
]


def simulate(prod, caja, cajon, base, trend, user_id, start, rng, leave_low):
    caja_qty = cajon_qty = 0
    movs = []

    def log(tipo, qty, origen, destino, when):
        movs.append(m.Movimiento(tipo=tipo, producto_id=prod.id, cantidad=qty, origen=origen,
                                 destino=destino, fecha_hora=when, usuario_id=user_id, es_simulado=True))

    for day in range(DAYS):
        when = start + timedelta(days=day, hours=9)
        if caja_qty < 60:
            log("entrada", 400, None, caja.codigo_ubicacion, when)
            caja_qty += 400
        demand = max(0, int(rng.gauss(base + trend * day, 2)))
        if demand == 0:
            continue
        if cajon_qty < demand:
            refill = min(caja_qty, 80)
            log("traslado", refill, caja.codigo_ubicacion, cajon.codigo_ubicacion, when + timedelta(hours=1))
            caja_qty -= refill
            cajon_qty += refill
        qty = min(demand, cajon_qty)
        if qty > 0:
            log("salida", qty, cajon.codigo_ubicacion, None, when + timedelta(hours=3))
            cajon_qty -= qty
    if leave_low and cajon_qty > 5:
        log("salida", cajon_qty - 5, cajon.codigo_ubicacion, None, start + timedelta(days=DAYS - 1, hours=10))
        cajon_qty = 5
    return caja_qty, cajon_qty, movs


def main():
    print("ATENCIÓN: se borrarán TODAS las tablas de megasupply y se cargarán datos de prueba simulados.")
    if input("Escribe SI para continuar: ").strip() != "SI":
        print("Cancelado.")
        return
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    rng = random.Random(42)
    start = (datetime.now() - timedelta(days=DAYS)).replace(hour=0, minute=0, second=0, microsecond=0)
    with SessionLocal() as s:
        operario = m.Usuario(nombre="Operario Demo", rol="operario")
        encargado = m.Usuario(nombre="Encargado Demo", rol="encargado")
        cajas = {c: m.Caja(codigo_ubicacion=c, descripcion=f"Caja {c}") for c in ("A-01", "A-02")}
        cajones = {c: m.Cajon(codigo_ubicacion=c, capacidad=200, cantidad_minima=0)
                   for c in ("C-01", "C-02", "C-03")}
        s.add_all([operario, encargado, *cajas.values(), *cajones.values()])
        s.flush()
        prods = []
        for code, name, desc, minimo, base, trend, caja_c, cajon_c, low in PRODUCTS:
            p = m.Producto(codigo_qr=code, nombre=name, descripcion=desc, stock_minimo_cajon=minimo)
            s.add(p)
            s.flush()
            prods.append(p)
            caja, cajon = cajas[caja_c], cajones[cajon_c]
            caja_qty, cajon_qty, movs = simulate(p, caja, cajon, base, trend, operario.id, start, rng, low)
            s.add_all(movs)
            if caja_qty > 0:
                s.add(m.CajaProducto(caja_id=caja.id, producto_id=p.id, cantidad=caja_qty))
            if cajon_qty > 0:
                s.add(m.CajonProducto(cajon_id=cajon.id, producto_id=p.id, cantidad=cajon_qty))
        s.add(m.Pedido(producto_id=prods[0].id, cantidad_solicitada=50,
                       fecha_esperada=date.today() + timedelta(days=7), estado="pendiente"))
        s.commit()
    print("Listo: 3 productos, 2 cajas, 3 cajones, 2 usuarios y 120 días de movimientos SIMULADOS.")


if __name__ == "__main__":
    main()