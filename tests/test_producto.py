"""
Prueba manual de las funciones CRUD de Producto.
Ejecutar con: python -m tests.test_producto
"""

from src.inventario.producto import (
    crear_producto,
    obtener_producto_por_codigo,
    listar_productos,
    actualizar_producto,
    eliminar_producto,
)

print("Creando producto de prueba...")
producto = crear_producto("PROD-001", "Tela Algodón", "Rollo de tela de algodón", stock_minimo=15)
print(f"✅ Creado: {producto.id} - {producto.nombre}")

print("\nBuscando por código QR...")
encontrado = obtener_producto_por_codigo("PROD-001")
print(f"✅ Encontrado: {encontrado.nombre}")

print("\nListando todos los productos...")
for p in listar_productos():
    print(f"  - {p.id}: {p.nombre} ({p.codigo_qr})")

print("\nActualizando producto...")
actualizado = actualizar_producto(producto.id, descripcion="Rollo de tela de algodón 100%")
print(f"✅ Actualizado: {actualizado.descripcion}")

print("\nEliminando producto...")
eliminado = eliminar_producto(producto.id)
print(f"✅ Eliminado: {eliminado}")