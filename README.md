# MegaSupply

**Sistema de gestión de inventario con identificación por código QR e inteligencia artificial para empresas importadoras y comercializadoras.**

## Contenido

- [La iniciativa](#la-iniciativa)
- [Cómo funciona la bodega](#cómo-funciona-la-bodega)
- [Funcionalidades](#funcionalidades)
- [Inteligencia artificial](#inteligencia-artificial)
- [Estado del proyecto](#estado-del-proyecto)
- [Arquitectura](#arquitectura)
- [Modelo de datos](#modelo-de-datos)
- [Tecnologías](#tecnologías)
- [Instalación y ejecución](#instalación-y-ejecución)
- [Variables de entorno](#variables-de-entorno)
- [Uso rápido](#uso-rápido)
- [API](#api)
- [Datos abiertos colombianos](#datos-abiertos-colombianos)
- [Pruebas](#pruebas)
- [Seguridad y privacidad](#seguridad-y-privacidad)
- [Documentación y metodología](#documentación-y-metodología)
- [Hoja de ruta](#hoja-de-ruta)
- [Limitaciones conocidas](#limitaciones-conocidas)
- [Equipo](#equipo)

## La iniciativa

### Problema

Las empresa importadoras y comercializadoras, pierde tiempo en dos tareas: surtir los pedidos y registrar y controlar lo que hay en sus **cajas** (almacenamiento) y **cajones** (surtido). Cuando el control es manual, es difícil saber cuánta mercancía hay y dónde está, los faltantes se descubren cuando ya afectan un pedido y las decisiones de abastecimiento se toman por intuición y no con base en el historial.

### Propuesta

MegaSupply es un software de escritorio que registra cada entrada, traslado y salida de mercancía leyendo un código QR con una cámara, mantiene el inventario por ubicación y conserva un historial de movimientos. Con ese historial genera alertas, predice la demanda y sugiere cuánto reabastecer, siempre como apoyo: la persona decide.

### Objetivo general

Desarrollar un sistema de gestión de inventario que integre la identificación por código QR y un componente de inteligencia artificial que apoye las decisiones de abastecimiento de una empresa importadora.

### Objetivos específicos

- Registrar entradas, traslados y salidas leyendo un código QR, impidiendo siempre sacar más de lo disponible.
- Representar por separado las cajas y los cajones y los traslados entre ellos.
- Registrar los pedidos próximos y usarlos en el análisis de abastecimiento.
- Alertar cuando un cajón baje de su mínimo.
- Predecir la demanda desde el historial y convertirla en una recomendación que el usuario acepta, modifica o rechaza.
- Generar informes mensuales, con y sin apoyo de IA.

### Población objetivo

Beneficiarios directos: el personal de bodega, que escanea y registra, y los responsables de compras y abastecimiento de Mega Import. Beneficiarios indirectos: la administración y los clientes que reciben sus pedidos.

## Cómo funciona la bodega

La bodega tiene **dos espacios distintos que nunca se tratan como lo mismo**:

- **Cajas (almacenamiento):** donde llega y se guarda la mercancía importada.
- **Cajones (surtido):** de donde los trabajadores toman producto para armar pedidos.

```
Llega mercancía  ->  ENTRADA a una CAJA
                         |  TRASLADO cuando el cajón necesita reponerse
                         v
                     CAJÓN
                         |  SALIDA para un pedido
                         v
                     Mercancía despachada
```

Reglas: la **entrada** siempre suma a una caja, la **salida** siempre resta de un cajón, y el **traslado** se rechaza si la caja de origen no tiene stock. Cada operación es atómica y deja una fila en el historial. El QR contiene solo el código del producto (`PROD-001`); ubicaciones y cantidades se consultan en la base de datos.

## Funcionalidades

| Pestaña | Qué permite |
|---|---|
| **Escáner (Entrada / Salida)** | Cámara con lectura de QR, modo ENTRADA (caja destino) o SALIDA (cajón origen), código manual, registro automático de 1 unidad por escaneo |
| **Inventario y traslados** | Stock por caja y cajón, filas en rojo si el cajón está bajo el mínimo, traslado caja a cajón e historial |
| **Pedidos** | Crear pedidos próximos y marcarlos como completados |
| **Alertas y recomendaciones** | Alertas de reabastecimiento, recomendación por predicción de demanda, aceptar / modificar / rechazar, opinión opcional de Gemini |
| **Productos y QR** | Alta de productos con código sugerido, etiquetas QR imprimibles con código y nombre, exportación de todos los QR |
| **Informe y mercado** | Informe mensual, resumen del mes con IA, consulta del TRM y de precios de GNCV |

## Inteligencia artificial

La IA **apoya y nunca decide**: no se ejecuta ninguna acción automáticamente. El sistema separa tres tipos de lógica:

| Tipo | Dónde se usa |
|---|---|
| **Lógica tradicional** | Mínimos, sumas de stock, validación de salidas, nivel de riesgo y cantidad sugerida |
| **Machine Learning** | Regresión lineal (scikit-learn) sobre las salidas diarias para estimar la demanda de 30 días |
| **IA generativa (Gemini)** | Opinión puntual por producto y resumen mensual redactado |

**Recomendación:** `sugerida = demanda estimada + pedidos pendientes + mínimo − stock actual`. El riesgo es ALTO si el stock cubre menos de la mitad de lo necesario, MEDIO si cubre menos de todo y BAJO si alcanza. Cada recomendación guarda si se basó en datos **reales** o **simulados**.

**Resumen mensual con IA:** cada clic es una petición independiente, sin historial de chat. Hay tiempo límite por llamada, modelos de respaldo, caché de respuestas reales y, si la IA falla, un resumen local redactado con reglas a partir de los mismos datos, que indica el motivo del fallo. El usuario siempre recibe un resumen.

**Datos simulados:** el script `seed_demo` carga 120 días de movimientos de prueba marcados con `es_simulado = true`. No son datos reales de la empresa y se identifican así en la interfaz.

## Estado del proyecto

| Componente | Estado |
|---|---|
| Modelo de datos de 9 tablas con restricciones | Implementado |
| Lectura de QR con cámara integrada a la interfaz y etiquetas QR | Implementado |
| CRUD de productos | Implementado |
| Entradas a caja, salidas de cajón y traslados con validación de stock | Implementado |
| Pedidos próximos y alertas de reabastecimiento | Implementado |
| Predicción de demanda y recomendación revisable por el usuario | Implementado (entrenada con datos simulados) |
| Informe mensual | Implementado (texto) |
| Resumen mensual con IA y respaldo local | Implementado |
| Interfaz de escritorio (PyQt6) | Implementado |
| Arquitectura hexagonal con inyección de dependencias | Implementado |
| Datos abiertos (TRM y GNCV) con reintentos, circuit breaker y DuckDB | Implementado |
| Pruebas automáticas | Implementado |
| Dashboard con gráficos | Pendiente |
| Inicio de sesión y roles | Pendiente |
| Pantalla para crear cajas y cajones (hoy solo por la API) | Pendiente |
| Migración de `/api/ai/analyze` al puerto `AIAdvisor` | Pendiente |
| Entrenamiento con datos reales | Pendiente hasta acumular historial |

## Arquitectura

Monolito modular con arquitectura hexagonal. Las dependencias apuntan siempre hacia el dominio.

```
Ventana PyQt6 -> ApiClient (HTTP) -> routers FastAPI -> servicios -> repositorios -> PostgreSQL
```

```
src/
  domain/          entidades, errores de negocio y puertos (contratos)
  application/     servicios: productos, inventario, pedidos, abastecimiento,
                   recomendaciones, informes y resumen con IA
  infrastructure/  adaptadores: PostgreSQL, regresión lineal, Gemini,
                   cliente HTTP resiliente, datos abiertos, DuckDB
  api/             FastAPI: main, dependencies, routers y schemas
  db/              conexión, modelos SQLAlchemy y seed de datos de prueba
  ui/              ventana PyQt6, una pestaña por pantalla y etiquetas QR
  inventario/      CRUD anterior (código heredado)
tests/             pruebas automáticas y scripts manuales (cámara, QR, diagnósticos)
docs/              modelo entidad-relación, diccionario de datos, UML y guía del código
run.py             arranca la API en segundo plano y abre la interfaz
```

Contextos delimitados: **Catálogo** (identidad del producto), **Inventario** (cajas, cajones y movimientos) y **Abastecimiento y Análisis** (alertas, predicción, informes y fuentes externas). Se eligió un monolito modular por el tamaño del equipo y el costo operativo; la migración de rutas heredadas sigue el patrón Strangler Fig.

## Modelo de datos

| Tabla | Propósito |
|---|---|
| `producto` | Identidad (`codigo_qr` único) y stock mínimo en cajón |
| `caja` | Ubicación de almacenamiento |
| `cajon` | Ubicación de surtido, con capacidad y mínimo |
| `caja_producto` | Cantidad de cada producto en cada caja |
| `cajon_producto` | Cantidad de cada producto en cada cajón |
| `movimiento` | Historial de entradas, salidas y traslados (con `es_simulado`) |
| `pedido` | Pedidos próximos: producto, cantidad, fecha y estado |
| `usuario` | Persona que registra un movimiento |
| `recomendacion` | Sugerencias de abastecimiento y la decisión del usuario |

El stock de un producto es la suma de sus cantidades en cajas y cajones. Solo `movimiento` guarda historia.

## Tecnologías

| Capa | Tecnología |
|---|---|
| Lenguaje | Python |
| Interfaz | PyQt6, OpenCV, pyzbar, qrcode |
| API | FastAPI, Pydantic, Uvicorn |
| Base de datos | PostgreSQL, SQLAlchemy, psycopg2 |
| Machine Learning | scikit-learn |
| IA generativa | Google Gemini (`google-genai`) |
| Datos externos | httpx, DuckDB, pandas |
| Pruebas | pytest, httpx, SQLite en memoria |

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
6. Cargar datos de prueba: `python -m src.db.seed_demo`. **Borra todas las tablas de `megasupply`**; no lo ejecutes si ya hay datos que quieras conservar.
7. Iniciar la aplicación: `python run.py`

`run.py` levanta la API en segundo plano y abre la ventana. La documentación interactiva de la API queda en `http://127.0.0.1:8000/docs` mientras la aplicación está abierta.

## Variables de entorno

| Variable | Obligatoria | Descripción |
|---|---|---|
| `DB_PASSWORD` | Sí | Contraseña del usuario `postgres` |
| `GEMINI_API_KEY` | No | Habilita la opinión y el resumen con IA; sin ella, el resumen usa reglas locales |
| `GEMINI_MODELS` | No | Modelos en orden de preferencia, separados por coma |
| `GEMINI_THINKING_LEVEL` | No | Opcional: `low` reduce el tiempo de razonamiento |
| `REPORT_CONTEXT` | No | Contexto de la empresa para el resumen con IA |

El archivo `.env` nunca se sube al repositorio.

## Uso rápido

1. **Productos y QR:** crea un producto; se genera su etiqueta en `qr_generados/`.
2. **Escáner en ENTRADA:** elige una caja, muestra el QR y confirma la cantidad.
3. **Inventario y traslados:** traslada mercancía de la caja al cajón.
4. **Escáner en SALIDA:** elige un cajón y registra la salida; si pides más de lo que hay, se rechaza.
5. **Alertas y recomendaciones:** genera una recomendación y acéptala, modifícala o recházala.
6. **Informe y mercado:** genera el informe mensual o el resumen con IA.

## API

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/health` | Estado del servicio |
| POST / GET | `/api/products/` | Crear y listar productos |
| GET | `/api/products/code/{codigo_qr}` | Buscar por código QR |
| GET / PUT / DELETE | `/api/products/{id}` | Consultar, actualizar y eliminar |
| POST | `/api/inventory/entry` · `/exit` · `/transfer` | Entrada a caja, salida de cajón y traslado |
| GET | `/api/inventory/stock/{codigo_qr}` · `/snapshot` · `/movements` | Stock, inventario completo e historial |
| GET / POST | `/api/inventory/cajas` · `/cajones` | Listar y crear ubicaciones |
| POST / GET | `/api/orders/` | Crear y listar pedidos |
| PUT | `/api/orders/{id}/state` | Cambiar el estado de un pedido |
| GET | `/api/replenishment/alerts` · `/{codigo_qr}` | Alertas y evaluación por producto |
| POST | `/api/recommendations/generate/{codigo_qr}` | Generar una recomendación |
| GET | `/api/recommendations/` | Listar recomendaciones |
| POST | `/api/recommendations/{id}/decision` | Aceptar, modificar o rechazar |
| GET | `/api/reports/monthly` · `/monthly/ai` | Informe mensual y resumen con IA |
| GET | `/api/market/trm` · `/gncv` | Estadísticas del TRM y de precios de GNCV |
| POST | `/api/ai/analyze` | Análisis con Gemini (ruta heredada) |

## Datos abiertos colombianos

- **TRM**, Superintendencia Financiera: `datos.gov.co/resource/32sa-8pi3`. El costo de la mercancía importada depende del dólar.
- **Precios de GNCV**, Ministerio de Minas y Energía (SICOM): `datos.gov.co/resource/he3q-86dn`, licencia CC BY-SA 4.0. El combustible influye en el transporte y la distribución.

El consumo usa timeout de 18 s, reintentos con espera exponencial y un circuit breaker de tres estados (cerrado, abierto y semiabierto). Los datos se analizan con DuckDB.

## Pruebas

```
pytest -q
```

`pytest.ini` limita la ejecución a las pruebas automáticas, que usan SQLite en memoria y no necesitan PostgreSQL, internet ni cámara. Cubren el flujo de inventario, la predicción, la API, el circuit breaker y el resumen con IA. Los scripts de cámara, QR y diagnóstico se ejecutan a mano, por ejemplo `python tests/test_qr.py` o `python -m tests.diagnostico_gemini`.

## Seguridad y privacidad

- Llaves y contraseñas viven en `.env`, fuera del repositorio.
- Los datos de entrada se validan con Pydantic y las restricciones de la base de datos.
- El TRM y el GNCV son datos agregados y no personales. El campo de usuario de los movimientos sí identifica a una persona y se rige por la Ley 1581 de 2012.
- La reutilización de datos abiertos respeta la Ley 1712 de 2014 y la licencia de cada conjunto.

## Documentación y metodología

- `docs/`: modelo entidad-relación, diccionario de datos (referencia ISO/IEC 11179), diagramas UML y `guia_del_codigo.md`.
- **Gestión:** tablero Kanban en Trello con listas de estado y etiquetas de tipo.
- **Control de versiones:** una rama por funcionalidad, Pull Request hacia `main` y commits pequeños.
- **Código:** docstrings en cada función y clase, y pruebas automáticas.

## Hoja de ruta

1. Dashboard con gráficos.
2. Inicio de sesión y roles (operario y encargado).
3. Pantalla para crear cajas y cajones.
4. Reentrenar la predicción con datos reales.
5. Migrar `/api/ai/analyze` al puerto `AIAdvisor`.
6. Evaluar el sistema con los trabajadores de la empresa.

## Limitaciones conocidas

- La predicción se entrenó con datos simulados; sus cifras no representan a la empresa.
- No hay autenticación: el movimiento no registra qué usuario lo hizo.
- El informe es textual, sin gráficos.
- Los nombres de los modelos de Gemini cambian con el tiempo y deben verificarse con la llave propia.
