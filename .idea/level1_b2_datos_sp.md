# Parte B.2 — Modelo de datos (DER + Diccionario de datos)

## Entidades y relaciones

**Entidades:**
- **Producto** — artículo en el inventario
- **Venta** — registro de una venta realizada
- **DetalleVenta** — ítems dentro de una venta (tabla intermedia)
- **Evento** — feria o ubicación donde opera el foodtruck

**Cardinalidades:**
- `Evento` **1:N** `Venta` — un evento contiene muchas ventas
- `Venta` **1:N** `DetalleVenta` — una venta contiene muchos ítems
- `Producto` **1:N** `DetalleVenta` — un producto aparece en distintos ítems
- La relación `Venta` **N:M** `Producto` se implementa a través de `DetalleVenta`

---

## Diccionario de datos — 3 entidades críticas

### Producto

| Campo | Tipo | Descripción |
|---|---|---|
| id_producto | INT (PK) | Identificador único del producto |
| nombre | VARCHAR(100) | Nombre del producto |
| precio | DECIMAL(10,2) | Precio unitario de venta |
| stock | INT | Cantidad disponible en inventario |
| stock_minimo | INT | Umbral mínimo para generar alerta |

### Venta

| Campo | Tipo | Descripción |
|---|---|---|
| id_venta | INT (PK) | Identificador único de la venta |
| fecha | DATETIME | Fecha y hora del registro |
| total | DECIMAL(10,2) | Monto total de la venta |
| id_evento | INT (FK) | Evento en el que se realizó la venta |

### Evento

| Campo | Tipo | Descripción |
|---|---|---|
| id_evento | INT (PK) | Identificador único del evento |
| nombre | VARCHAR(100) | Nombre de la feria o evento |
| ubicacion | VARCHAR(200) | Dirección o descripción del lugar |
| fecha | DATE | Fecha del evento |
| pronostico_clima | VARCHAR(50) | Pronóstico obtenido de la API del clima |
