# Modelo de base de datos para MegaSupply.

# Importamos las librerías necesarias para definir los modelos de la base de datos.
from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey

# Importamos la base de datos desde el archivo database.py.
from src.db.database import Base
# "Base" es la clase base para todos los modelos de la base de datos. Heredamos de esta clase
# para crear nuestras tablas con un molde especial para la base de datos.

# Definimos la tabla "productos" que representa los productos en la base de datos.
class Producto(Base): # -> Creamos la tabla "producto" en la base de datos.

    __tablename__ = "producto" # La nombramos como "producto" en la base de datos.

    id = Column(Integer, primary_key=True) 
    # "id" sera una columna de tipo entera y sera la clave primaria de la tabla.

    codigo_qr = Column(String, unique=True, nullable=False)
    # "codigo_qr" sera una columna de tipo string, sera unica y no podra ser nula.

    nombre = Column(String, nullable=False)
    # "nombre" sera una columna de tipo string y no podra ser nula.

    descripcion = Column(String)
    # "descripcion" sera una columna de tipo string y podra ser nula.

    stock_minimo_cajon = Column(Integer, default=0)
    # "stock_minimo_cajon" sera una columna de tipo entera y tendra un valor por defecto de 0.

# Definimos la tabla "caja" que representa las cajas de almacenamiento en la base de datos.
class Caja(Base):

    __tablename__ = "caja" # La nombramos como "caja" en la base de datos.

    id = Column(Integer, primary_key=True)
    # "id" sera una columna de tipo entera y sera la clave primaria de la tabla.

    codigo_ubicacion = Column(String, nullable=False)
    # "codigo_ubicacion" sera una columna de tipo string y no podra ser nula.

    descripcion = Column(String)
    # "descripcion" sera una columna de tipo string y podra ser nula.

# Definimos la tabla "caja_producto" que representa la relación entre cajas y productos en la base de datos.
class CajaProducto(Base):

    __tablename__ = "caja_producto"# La nombramos como "caja_producto" en la base de datos.

    caja_id = Column(Integer, ForeignKey("caja.id"), primary_key=True)
    # "caja_id" sera una columna de tipo entera, sera una clave foranea que hace referencia a la 
    # tabla "caja" y sera la clave primaria de la tabla.

    producto_id = Column(Integer, ForeignKey("producto.id"), primary_key=True)
    # "producto_id" sera una columna de tipo entera, sera una clave foranea que hace referencia a la
    # tabla "producto" y sera la clave primaria de la tabla.

    cantidad = Column(Integer, default=0)
    # "cantidad" sera una columna de tipo entera y tendra un valor por defecto de 0.

# Definimos la tabla "cajon" que representa los cajones de almacenamiento en la base de datos.
class Cajon(Base):

    __tablename__ = "cajon" # La nombramos como "cajon" en la base de datos.

    id = Column(Integer, primary_key=True)
    # "id" sera una columna de tipo entera y sera la clave primaria de la tabla.

    codigo_ubicacion = Column(String, nullable=False)
    # "codigo_ubicacion" sera una columna de tipo string y no podra ser nula.

    capacidad = Column(Integer)
    # "capacidad" sera una columna de tipo entera y podra ser nula.

    cantidad_minima = Column(Integer, default=0)
    # "cantidad_minima" sera una columna de tipo entera y tendra un valor por defecto de 0.

# Definimos la tabla "cajon_producto" que representa la relación entre cajones y productos en la db.
class CajonProducto(Base):

    __tablename__ = "cajon_producto" 
    # La nombramos como "cajon_producto" en la base de datos.

    cajon_id = Column(Integer, ForeignKey("cajon.id"), primary_key=True)
    # "cajon_id" sera una columna de tipo entera, sera una clave foranea que hace referencia a la
    # tabla "cajon" y sera la clave primaria de la tabla.

    producto_id = Column(Integer, ForeignKey("producto.id"), primary_key=True)
    # "producto_id" sera una columna de tipo entera, sera una clave foranea que hace referencia a la
    # tabla "producto" y sera la clave primaria de la tabla.

    cantidad = Column(Integer, default=0)
    # "cantidad" sera una columna de tipo entera y tendra un valor por defecto de 0.

# Definimos la tabla "usuario" que representa los usuarios en la base de datos.
class Usuario(Base):

    __tablename__ = "usuario"# La nombramos como "usuario" en la base de datos.

    id = Column(Integer, primary_key=True)
    # "id" sera una columna de tipo entera y sera la clave primaria de la tabla.

    nombre = Column(String, nullable=False)
    # "nombre" sera una columna de tipo string y no podra ser nula.
    
    rol = Column(String)
    # "rol" sera una columna de tipo string y podra ser nula.

# Definimos la tabla "movimiento" que representa los movimientos de productos en la base de datos.
class Movimiento(Base):

    __tablename__ = "movimiento"# La nombramos como "movimiento" en la base de datos.

    id = Column(Integer, primary_key=True)
    # "id" sera una columna de tipo entera y sera la clave primaria de la tabla.

    tipo = Column(String, nullable=False)
    # "tipo" sera una columna de tipo string y no podra ser nula.

    producto_id = Column(Integer, ForeignKey("producto.id"), nullable=False)
    # "producto_id" sera una columna de tipo entera, sera una clave foranea que hace referencia a la
    # tabla "producto" y no podra ser nula.

    cantidad = Column(Integer, nullable=False)
    # "cantidad" sera una columna de tipo entera y no podra ser nula.

    origen = Column(String)
    # "origen" sera una columna de tipo string y podra ser nula.

    destino = Column(String)
    # "destino" sera una columna de tipo string y podra ser nula.

    fecha_hora = Column(DateTime, nullable=False)
    # "fecha_hora" sera una columna de tipo DateTime y no podra ser nula.

    usuario_id = Column(Integer, ForeignKey("usuario.id"))
    # "usuario_id" sera una columna de tipo entera, sera una clave foranea que hace referencia a la
    # tabla "usuario" y podra ser nula.

# Definimos la tabla "pedido" que representa los pedidos de productos en la base de datos.
class Pedido(Base):

    __tablename__ = "pedido" # La nombramos como "pedido" en la base de datos.

    id = Column(Integer, primary_key=True)
    # "id" sera una columna de tipo entera y sera la clave primaria de la tabla.

    producto_id = Column(Integer, ForeignKey("producto.id"), nullable=False)
    # "producto_id" sera una columna de tipo entera, sera una clave foranea que hace referencia a la
    # tabla "producto" y no podra ser nula.

    cantidad_solicitada = Column(Integer, nullable=False)
    # "cantidad_solicitada" sera una columna de tipo entera y no podra ser nula.

    fecha_esperada = Column(Date)
    # "fecha_esperada" sera una columna de tipo Date y podra ser nula.

    estado = Column(String, default="pendiente")
    # "estado" sera una columna de tipo string y tendra un valor por defecto de "pendiente".