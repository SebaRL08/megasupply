"""Modelos SQLAlchemy de MegaSupply: 8 tablas del diccionario de datos más 'recomendacion'."""
from sqlalchemy import (Boolean, CheckConstraint, Column, Date, DateTime, ForeignKey,
                        Index, Integer, String)
from src.db.database import Base


class Producto(Base):
    __tablename__ = "producto"
    id = Column(Integer, primary_key=True)
    codigo_qr = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(255))
    stock_minimo_cajon = Column(Integer, nullable=False, default=0)
    __table_args__ = (CheckConstraint("stock_minimo_cajon >= 0", name="ck_producto_minimo"),)


class Caja(Base):
    __tablename__ = "caja"
    id = Column(Integer, primary_key=True)
    codigo_ubicacion = Column(String(20), unique=True, nullable=False)
    descripcion = Column(String(255))


class CajaProducto(Base):
    __tablename__ = "caja_producto"
    caja_id = Column(Integer, ForeignKey("caja.id"), primary_key=True)
    producto_id = Column(Integer, ForeignKey("producto.id"), primary_key=True)
    cantidad = Column(Integer, nullable=False, default=0)
    __table_args__ = (CheckConstraint("cantidad >= 0", name="ck_caja_producto_cantidad"),)


class Cajon(Base):
    __tablename__ = "cajon"
    id = Column(Integer, primary_key=True)
    codigo_ubicacion = Column(String(20), unique=True, nullable=False)
    capacidad = Column(Integer)
    cantidad_minima = Column(Integer, nullable=False, default=0)
    __table_args__ = (
        CheckConstraint("capacidad IS NULL OR capacidad > 0", name="ck_cajon_capacidad"),
        CheckConstraint("cantidad_minima >= 0", name="ck_cajon_minima"),
    )


class CajonProducto(Base):
    __tablename__ = "cajon_producto"
    cajon_id = Column(Integer, ForeignKey("cajon.id"), primary_key=True)
    producto_id = Column(Integer, ForeignKey("producto.id"), primary_key=True)
    cantidad = Column(Integer, nullable=False, default=0)
    __table_args__ = (CheckConstraint("cantidad >= 0", name="ck_cajon_producto_cantidad"),)


class Usuario(Base):
    __tablename__ = "usuario"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    rol = Column(String(30))


class Movimiento(Base):
    __tablename__ = "movimiento"
    id = Column(Integer, primary_key=True)
    tipo = Column(String(20), nullable=False)  # entrada | salida | traslado
    producto_id = Column(Integer, ForeignKey("producto.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    origen = Column(String(20))
    destino = Column(String(20))
    fecha_hora = Column(DateTime, nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuario.id"))
    es_simulado = Column(Boolean, nullable=False, default=False)  # True = dato de prueba
    __table_args__ = (
        CheckConstraint("tipo IN ('entrada','salida','traslado')", name="ck_movimiento_tipo"),
        CheckConstraint("cantidad > 0", name="ck_movimiento_cantidad"),
        Index("ix_movimiento_producto_fecha", "producto_id", "fecha_hora"),
    )


class Pedido(Base):
    __tablename__ = "pedido"
    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, ForeignKey("producto.id"), nullable=False)
    cantidad_solicitada = Column(Integer, nullable=False)
    fecha_esperada = Column(Date)
    estado = Column(String(20), nullable=False, default="pendiente")
    __table_args__ = (
        CheckConstraint("cantidad_solicitada > 0", name="ck_pedido_cantidad"),
        CheckConstraint("estado IN ('pendiente','completado')", name="ck_pedido_estado"),
    )


class Recomendacion(Base):
    """Sugerencia de abastecimiento. El usuario la acepta, modifica o rechaza."""
    __tablename__ = "recomendacion"
    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, ForeignKey("producto.id"), nullable=False)
    fecha_hora = Column(DateTime, nullable=False)
    stock_actual = Column(Integer, nullable=False)
    demanda_estimada = Column(Integer, nullable=False)
    pedidos_pendientes = Column(Integer, nullable=False)
    cantidad_sugerida = Column(Integer, nullable=False)
    nivel_riesgo = Column(String(10), nullable=False)
    datos_base = Column(String(10), nullable=False)  # 'real' o 'simulado'
    estado = Column(String(20), nullable=False, default="pendiente")
    cantidad_final = Column(Integer)
    __table_args__ = (CheckConstraint(
        "estado IN ('pendiente','aceptada','modificada','rechazada')", name="ck_recomendacion_estado"),)