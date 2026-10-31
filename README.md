# MegaSupply

**Sistema de gestión de inventario con identificación por código QR e inteligencia artificial para empresas importadoras y comercializadoras.**
Proyecto de Ingeniería de Software, Universidad Manuela Beltrán.

## Contenido

- [La iniciativa](#la-iniciativa)
- [Cómo funciona la bodega](#cómo-funciona-la-bodega)
- [Flujo del sistema](#flujo-del-sistema)
- [Inteligencia artificial](#inteligencia-artificial)
- [Estado del proyecto](#estado-del-proyecto)
- [Arquitectura](#arquitectura)
- [Modelo de datos](#modelo-de-datos)
- [Tecnologías](#tecnologías)
- [Instalación y ejecución](#instalación-y-ejecución)
- [Endpoints](#endpoints)
- [Datos abiertos colombianos](#datos-abiertos-colombianos)
- [Seguridad y privacidad](#seguridad-y-privacidad)
- [Metodología y documentación](#metodología-y-documentación)
- [Hoja de ruta](#hoja-de-ruta)
- [Limitaciones conocidas](#limitaciones-conocidas)
- [Equipo](#equipo)

## La iniciativa

### Problema

Las empresas importadoras y comercializadoras suelen controlar su inventario de forma manual o con herramientas dispersas. Esto genera tres problemas: no se sabe con exactitud cuánta mercancía hay y dónde está, los faltantes se descubren cuando ya afectan un pedido, y las decisiones de abastecimiento se toman por intuición y no con base en el historial de movimientos.

### Propuesta

MegaSupply es un software de escritorio que registra cada entrada y salida de mercancía mediante la lectura de un código QR con una cámara o webcam, mantiene el inventario actualizado en una base de datos y conserva un historial de movimientos. Con ese historial, el sistema apoyará la anticipación de faltantes y las decisiones de abastecimiento.

### Objetivo general

Desarrollar un sistema de gestión de inventario que integre la identificación por código QR y un componente de inteligencia artificial que apoye las decisiones de abastecimiento de una empresa importadora.

### Objetivos específicos

- Registrar entradas y salidas de mercancía a partir de la lectura de un código QR, impidiendo siempre sacar más de lo disponible.
- Representar por separado las dos zonas físicas de la bodega (cajas y cajones) y los traslados entre ellas.
- Registrar los pedidos próximos para usarlos en el análisis de abastecimiento.
- Generar alertas de reabastecimiento cuando un cajón baje de su mínimo.
- Predecir la demanda de cada producto a partir del historial de movimientos y convertirla en una recomendación revisable por el usuario.
- Generar informes mensuales de demanda, productos próximos a agotarse y abastecimiento recomendado.

### Población objetivo

El personal de bodega, que escanea y registra los movimientos, y los encargados de compras y abastecimiento de pequeñas y medianas empresas importadoras o comercializadoras, que necesitan decidir cuánto y cuándo pedir.

## Cómo funciona la bodega

El diseño respeta la organización física real de la bodega, que tiene **dos espacios distintos que nunca deben tratarse como lo mismo**:

- **Cajas (zona de almacenamiento):** es donde llega y se guarda la mercancía que la empresa importa. Es el stock de fondo.
- **Cajones (zona de surtido):** es el punto desde el cual los trabajadores toman producto para armar los pedidos.

```
Llega mercancía  ->  CAJAS (almacenamiento)
                         |
                         |  traslado cuando el cajón necesita reponerse
                         v
                     CAJONES (surtido)
                         |
                         |  un trabajador toma producto para un pedido
                         v
                     SALIDA registrada
```

Ejemplo: la caja A-01 tiene 100 unidades del producto `PROD-001`. Se trasladan 20 al cajón C-05. Resultado: la caja A-01 queda con 80 y el cajón C-05 con 20, y el traslado queda registrado con fecha y hora.

## Flujo del sistema

```
Cámara -> lectura del QR -> identificación del producto
       -> selección de ENTRADA o SALIDA -> cantidad
       -> actualización del inventario -> registro del movimiento
```

El QR contiene únicamente un identificador único del producto (por ejemplo `PROD-001`). La ubicación y las cantidades no van en el QR, porque cambian constantemente y el código impreso no se reimprime; el sistema las consulta en la base de datos.

## Inteligencia artificial

La IA tiene una función real pero acotada: **apoyar la decisión, nunca tomarla**. El usuario siempre puede revisar, aceptar o modificar una recomendación, y no se ejecuta ninguna acción automáticamente.

El sistema separa tres tipos de lógica:

- **Lógica tradicional:** reglas como el stock mínimo, la suma de inventario o la validación de salidas.
- **Machine Learning (planeado):** un modelo simple de predicción de demanda (regresión lineal o promedio móvil) entrenado con el historial de movimientos. Mientras no exista historial real, se usarán datos simulados, documentados siempre como datos de prueba y nunca presentados como reales.
- **IA generativa (implementado, heredado):** un asistente con Google Gemini que analiza consultas de inventario y responde en formato JSON.

## Estado del proyecto

| Componente | Estado |
|---|---|
| Modelo de datos de 8 tablas en PostgreSQL | Implementado |
| Lectura de QR con cámara (OpenCV + pyzbar) y generación de QR de prueba | Implementado como scripts |
| CRUD de productos | Implementado |
| Registro de entradas y salidas con validación de stock | Implementado |
| Arquitectura hexagonal con inyección de dependencias | Implementado |
| Consumo resiliente de datos abiertos (TRM y GNCV) con DuckDB | Implementado |
| Asistente de IA con Gemini | Implementado (ruta heredada) |
| Pruebas automáticas | Implementado |
| Conexión de la cámara/QR con la API | Pendiente |
| Traslado caja a cajón y actualización de `caja_producto` y `cajon_producto` | Pendiente |
| Pedidos próximos y alertas de reabastecimiento | Pendiente |
| Interfaz de escritorio (PyQt6) | Pendiente |
| Predicción de demanda con Machine Learning | Pendiente |
| Informe mensual y dashboard | Pendiente |

## Arquitectura

Monolito modular con arquitectura hexagonal. Las dependencias apuntan siempre hacia el dominio.

```
src/
  domain/          entidades, errores de negocio y puertos (contratos)
  application/     servicios: ProductService, InventoryService, ReplenishmentService
  infrastructure/  adaptadores: PostgreSQL, memoria, Gemini, cliente HTTP resiliente, DuckDB
  api/             FastAPI: main, dependencies, routers, schemas
  db/              conexión y modelos SQLAlchemy
  inventario/      CRUD anterior (código heredado)
  qr/ pedidos/ abastecimiento/ ia/ ui/   módulos planeados
tests/             pruebas automáticas y scripts manuales (cámara, QR)
docs/              modelo entidad-relación y diagramas
```

Bounded contexts: **Catálogo** (identidad del producto), **Inventario** (cuánto hay y dónde, con cajas y cajones) y **Abastecimiento y Análisis** (cuándo y cuánto pedir, con datos externos e IA).

Se eligió un monolito modular en lugar de microservicios por el tamaño del equipo y el costo operativo. La migración de rutas heredadas sigue el patrón Strangler Fig.

## Modelo de datos

| Tabla | Propósito |
|---|---|
| `producto` | Identidad del producto (`codigo_qr` único) y stock mínimo en cajón |
| `caja` | Ubicación de almacenamiento |
| `cajon` | Ubicación de surtido, con capacidad y cantidad mínima |
| `caja_producto` | Cantidad de cada producto en cada caja |
| `cajon_producto` | Cantidad de cada producto en cada cajón |
| `movimiento` | Historial de entradas, salidas y traslados (única tabla con historia) |
| `pedido` | Pedidos próximos: producto, cantidad, fecha esperada y estado |
| `usuario` | Persona que registra cada movimiento |

El stock de un producto no se guarda como un campo: se calcula a partir de los movimientos (y, cuando se complete el traslado, de las tablas intermedias).

## Tecnologías

| Capa | Tecnología |
|---|---|
| Lenguaje | Python |
| API | FastAPI, Pydantic, Uvicorn |
| Base de datos | PostgreSQL, SQLAlchemy, psycopg2 |
| QR y cámara | OpenCV, pyzbar, qrcode |
| Análisis de datos | DuckDB, pandas |
| IA | Google Gemini (`google-genai`); scikit-learn planeado |
| Pruebas | pytest, httpx |
| Interfaz de escritorio | PyQt6 (planeado) |

## Instalación y ejecución

1. Clonar el repositorio y entrar a la carpeta.
2. Crear y activar el entorno virtual:
   ```
   py -m venv venv
   venv\Scripts\activate
   ```
3. Instalar dependencias: `pip install -r requirements.txt`
4. Crear la base de datos `megasupply` en PostgreSQL local.
5. Copiar la plantilla y completar tus datos: `copy .env.example .env`
6. Crear las tablas: `python -m tests.crear_tablas`
7. Iniciar la API:
   ```
   uvicorn src.api.main:app --reload
   ```
   Documentación interactiva en `http://127.0.0.1:8000/docs`.

**Pruebas:** `pytest -q`. El archivo `pytest.ini` limita la ejecución a las pruebas automáticas; los scripts de cámara y QR se ejecutan a mano, por ejemplo `python tests/test_qr.py`.

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| POST/GET/PUT/DELETE | `/api/products` | CRUD de productos |
| POST | `/api/inventory/entry` | Registrar entrada |
| POST | `/api/inventory/exit` | Registrar salida (409 si no hay stock) |
| GET | `/api/inventory/stock/{codigo_qr}` | Consultar stock |
| GET | `/api/replenishment/{codigo_qr}` | Evaluar reabastecimiento (`use_ai=true` opcional) |
| GET | `/api/market/trm` | Estadísticas del TRM |
| GET | `/api/market/gncv` | Precios de GNCV por departamento |
| POST | `/api/ai/analyze` | Análisis con Gemini (ruta heredada) |

## Datos abiertos colombianos

- **TRM**, Superintendencia Financiera: `datos.gov.co/resource/32sa-8pi3`. Relevante porque el costo de la mercancía importada depende del dólar.
- **Precios de GNCV**, Ministerio de Minas y Energía (SICOM): `datos.gov.co/resource/he3q-86dn`, licencia CC BY-SA 4.0. Relevante por su efecto en el transporte y la distribución.

El consumo usa un cliente HTTP resiliente: timeout de 5 segundos, hasta 3 reintentos con backoff exponencial y un circuit breaker de tres estados (cerrado, abierto y semiabierto). Los datos se analizan con DuckDB (conteo, promedio, mínimo, máximo, desviación estándar, `GROUP BY` y `HAVING`).

## Seguridad y privacidad

- Las llaves y contraseñas viven en `.env`, que no se sube al repositorio; `.env.example` es solo una plantilla.
- Los datos de entrada se validan con Pydantic y los parámetros enviados a servicios externos se validan antes de usarse.
- Los datos del TRM y del GNCV son agregados y no personales. El campo de usuario de los movimientos sí identifica a una persona, por lo que su tratamiento se rige por la Ley 1581 de 2012.
- La reutilización de datos abiertos respeta la Ley 1712 de 2014 y las licencias de cada conjunto.

## Metodología y documentación

- **Gestión:** tablero Kanban en Trello con listas de estado (Backlog, Análisis y Diseño, En Desarrollo, Pruebas, Correcciones, Terminado) y etiquetas de tipo (Backend, Frontend, Base de datos, IA, QR/Cámara, Bug, Documentación, MVP).
- **Control de versiones:** una rama por funcionalidad (`feature/...`), Pull Request hacia `main` y commits pequeños por tarea.
- **Código:** docstrings en cada función y clase, y pruebas automáticas con repositorios en memoria.
- **Documentación:** modelo entidad-relación, diccionario de datos (referencia ISO/IEC 11179) y diagramas UML (casos de uso, clases y componentes) en `docs/`.

## Hoja de ruta

1. Completar el traslado caja a cajón y la actualización de las tablas de ubicación.
2. Conectar la cámara y el QR con la API.
3. Construir la interfaz de escritorio con PyQt6.
4. Registrar pedidos próximos y generar alertas de reabastecimiento.
5. Crear un dataset simulado documentado y un modelo de predicción de demanda.
6. Generar la recomendación de abastecimiento y el informe mensual.
7. Migrar la ruta de IA heredada al puerto `AIAdvisor`.

## Limitaciones conocidas

- El stock se calcula desde la tabla `movimiento`; falta actualizar `caja_producto` y `cajon_producto`.
- La cámara y el QR aún funcionan como scripts independientes de la API.
- El modelo de Machine Learning no está implementado; no hay historial real suficiente.
- La ruta de IA con Gemini sigue como código heredado.
