# Operaciones CRUD para la entidad Producto
from src.db.database import SessionLocal # -> Sesiones para interactuar con la base de datos
from src.db.models import Producto # -> Modelo de la tabla "producto" en la base de datos

# Función para crear un nuevo producto en la base de datos
def crear_producto(codigo_qr: str, nombre: str, descripcion: str = "", stock_minimo: int = 0):

    sesion = SessionLocal() #Aqui el programa crea una nueva sesión para interactuar con la base de datos
    try: # Le decimos que intente ejecutar el siguiente bloque de código, y 
         #si ocurre un error, se ejecutará el bloque "finally"

        # Creamos un nuevo objeto Producto con los datos proporcionados
        nuevo_producto = Producto( 
            codigo_qr=codigo_qr,
            nombre=nombre,
            descripcion=descripcion,
            stock_minimo_cajon=stock_minimo,
        )

        # Agregamos el nuevo producto a la sesión y confirmamos los cambios en la base de datos 
        sesion.add(nuevo_producto) # Agregamos el nuevo producto a la sesión
        sesion.commit() # Confirmamos los cambios en la base de datos
        sesion.refresh(nuevo_producto) # Refrescamos el objeto para obtener los datos actualizados de la base de datos
        return nuevo_producto # Devolvemos el nuevo producto creado
    
    finally: # Cerramos la sesión para liberar recursos, independientemente de si ocurrió un error o no
        sesion.close() # Cerramos la sesión para liberar recursos

# Función para obtener un producto por su código QR
def obtener_producto_por_codigo(codigo_qr: str):

    sesion = SessionLocal()# Creamos una nueva sesión para interactuar con la base de datos
    try: # Le decimos que intente ejecutar el siguiente bloque de código, y
         #si ocurre un error, se ejecutará el bloque "finally"

        return sesion.query(Producto).filter(Producto.codigo_qr == codigo_qr).first()
        # Devolvemos el primer producto que coincida con el código QR proporcionado, o None si no se encuentra ninguno

    finally: # Cerramos la sesión para liberar recursos, independientemente de si ocurrió un error o no
        sesion.close() # Cerramos la sesión para liberar recursos

# Función para listar todos los productos en la base de datos
def listar_productos():# Creamos una nueva sesión para interactuar con la base de datos

    sesion = SessionLocal() # Creamos una nueva sesión para interactuar con la base de datos
    try:
        return sesion.query(Producto).all() # Devolvemos todos los productos en la base de datos como una lista de objetos Producto
    finally:
        sesion.close()

# Función para actualizar un producto existente en la base de datos
def actualizar_producto(producto_id: int, **campos):# Creamos una nueva sesión para interactuar con la base de datos

    sesion = SessionLocal()
    try:

# Buscamos el producto por su ID y actualizamos los campos proporcionados       
        producto = sesion.query(Producto).filter(Producto.id == producto_id).first()
# Si no se encuentra el producto, devolvemos None
        if producto is None:
            return None
# Actualizamos los campos del producto con los valores proporcionados
        for campo, valor in campos.items():
            setattr(producto, campo, valor) # Actualizamos el atributo del producto con el valor proporcionado

        sesion.commit() # Confirmamos los cambios en la base de datos
        sesion.refresh(producto)# Refrescamos el objeto para obtener los datos actualizados de la base de datos
        return producto # Devolvemos el producto actualizado
    finally:
        sesion.close()

# Función para eliminar un producto de la base de datos
def eliminar_producto(producto_id: int):

    sesion = SessionLocal()
    try:
        producto = sesion.query(Producto).filter(Producto.id == producto_id).first()
        if producto is None:
            return False
        sesion.delete(producto)
        sesion.commit()
        return True
    finally:
        sesion.close()