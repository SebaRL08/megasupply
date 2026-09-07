# Modelo entidad-relación — MegaSupply

Ver diagrama completo en `docs/diagramas/modelo_entidad_relacion.png`.

## Entidades

**Producto**
Representa cada artículo que la empresa maneja en inventario. Se identifica de forma única por su `codigo_qr`, que es el mismo texto que lleva impreso el código QR físico. El stock real de un producto no se guarda como un campo directo aquí — se calcula sumando sus registros en CajaProducto y CajonProducto, para mantener trazabilidad de en qué ubicación física está cada unidad.

**Caja**
Ubicación física de almacenamiento general, donde llega y se guarda la mercancía recién importada.

**Cajón**
Ubicación física de surtido, desde donde los trabajadores toman producto para armar pedidos. Es un espacio físico distinto de las cajas, con su propia capacidad y cantidad mínima deseada.

**CajaProducto / CajonProducto**
Tablas intermedias que registran cuánta cantidad de un producto específico hay en una caja o cajón específico. Existen porque una caja/cajón puede contener varios productos distintos, y un producto puede estar repartido entre varias cajas/cajones a la vez — sin estas tablas intermedias, no sería posible representar esa relación de muchos-a-muchos.

**Movimiento**
Registro histórico de toda operación de inventario: entrada, salida o traslado entre caja y cajón. Es la única tabla que conserva historial completo; las tablas de CajaProducto y CajonProducto solo reflejan el estado actual, no el histórico.

**Pedido**
Solicitud próxima de producto, usada como insumo para el análisis de abastecimiento y la predicción de demanda.

**Usuario**
Persona que opera el sistema y registra movimientos, para trazabilidad de quién hizo cada operación.

## Decisiones de diseño relevantes

- Se separan explícitamente Caja y Cajón porque representan dos espacios físicos distintos en la bodega real, con propósitos distintos (almacenamiento vs. surtido).
- El QR únicamente contiene el identificador del producto (`codigo_qr`), nunca su ubicación o cantidad — esos datos cambian constantemente y se consultan en la base de datos, no en el código impreso.
- `Movimiento.origen` y `Movimiento.destino` son campos de texto genéricos que permiten representar los 3 tipos de operación (entrada solo tiene destino, salida solo tiene origen, traslado tiene ambos) sin necesitar tablas separadas por tipo.