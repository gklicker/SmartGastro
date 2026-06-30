# SmartGastro

MVP web para administrar inventario, menú y ventas de foodtrucks. El dashboard
integra el clima de Buenos Aires para ayudar a reducir las pérdidas de
mercadería durante jornadas con lluvia.

Trabajo Práctico Integrador de **Análisis y Metodología de Sistemas**.

## Funcionalidades

- Inicio y cierre de sesión con contraseña hasheada.
- Rutas de gestión protegidas.
- CRUD de ingredientes y existencias.
- Unidades de medida e iconos visuales para ingredientes y platos.
- Alertas de stock bajo.
- CRUD de productos del menú y recetas completas de múltiples ingredientes.
- Registro asíncrono de ventas con múltiples productos mediante `fetch()` y JSON.
- Descuento automático de ingredientes al vender.
- Historial, filtros, ranking, ingresos y ticket promedio.
- Pronóstico por lugar, fecha y hora con recomendaciones de producción.
- Persistencia relacional con SQLite y SQLAlchemy.

La versión de consola de la primera entrega continúa disponible en `cli.py`.
La segunda entrega se ejecuta desde `app.py`.

## Tecnologías

- Python 3
- Flask y Jinja
- Flask-SQLAlchemy
- SQLite
- HTML, CSS y JavaScript
- Open-Meteo API

## Instalación

### 1. Crear el entorno virtual

```bash
python -m venv .venv
```

### 2. Activarlo

Windows:

```bash
.venv\Scripts\activate
```

macOS o Linux:

```bash
source .venv/bin/activate
```

### 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar las variables de entorno

Copiar `.env.example` como `.env` y reemplazar `SECRET_KEY` por un valor
privado. El archivo `.env` nunca debe subirse al repositorio.

### 5. Crear la base y el usuario de demostración

```bash
flask --app app init-db
```

Para cargar ingredientes, recetas y ventas de ejemplo:

```bash
flask --app app seed-demo
```

Para reemplazar todos los datos locales por una demo limpia:

```bash
flask --app app seed-demo --reset
```

La carga normal es idempotente: no duplica información si la demo ya existe.

Si una base creada con una versión anterior tiene números de ticket fuera de
orden, se pueden ordenar cronológicamente sin borrar ventas:

```bash
flask --app app renumber-tickets
```

### 6. Ejecutar

```bash
flask --app app run
```

Abrir `http://127.0.0.1:5000`.

## Pruebas automáticas

Las pruebas usan una base SQLite temporal en memoria y no modifican los datos
de demostración ni la base local:

```bash
python -m unittest discover -s tests -v
```

Cubren autenticación, rutas protegidas, inventario, ingresos de mercadería,
ventas, descuento de stock, rollback, alertas y formato argentino de fecha.

## Credenciales de prueba

- Usuario: `admin`
- Contraseña: `SmartGastro2026!`

La contraseña puede cambiarse antes de crear la base mediante
`DEMO_PASSWORD` en `.env`.

## Modelo de datos

- `User`: usuarios autorizados.
- `Ingredient`: ingredientes, stock y nivel mínimo.
- `MenuItem`: productos disponibles para la venta.
- `RecipeIngredient`: consumo de ingredientes por unidad vendida.
- `Receipt`: cabecera de una venta.
- `ReceiptItem`: productos y cantidades de cada venta.

Las operaciones de creación, modificación, eliminación y venta se ejecutan con
`try/except`; ante un error se realiza `db.session.rollback()`. Las consultas
se construyen mediante el ORM, sin concatenar datos del usuario en SQL.

## Secretos y archivos locales

El repositorio excluye:

- `.env`
- bases `.db`, `.sqlite` y `.sqlite3`
- entornos virtuales
- cachés de Python

Solo `.env.example`, sin secretos reales, debe permanecer versionado.

## Datos de demostración

La demo incluye hamburguesas, cheeseburgers, hot dogs, papas fritas y bebidas,
con sus recetas completas. También crea ventas distribuidas en distintas fechas
para poder probar filtros, productos más vendidos, productos sin ventas y
ticket promedio sin tener que ingresar datos manualmente.
