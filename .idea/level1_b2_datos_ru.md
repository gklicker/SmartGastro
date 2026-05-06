# Часть B.2 — Модель данных (ER-диаграмма + словарь данных)

## Сущности и связи

**Сущности:**
- **Producto** — товар в инвентаре
- **Venta** — факт продажи
- **DetalleVenta** — позиции внутри продажи (связующая таблица)
- **Evento** — мероприятие / локация

**Кардинальности:**
- `Evento` **1:N** `Venta` — одно событие содержит много продаж
- `Venta` **1:N** `DetalleVenta` — одна продажа содержит много позиций
- `Producto` **1:N** `DetalleVenta` — один продукт встречается в разных позициях
- Связь `Venta` **N:M** `Producto` реализована через `DetalleVenta`

---

## Словарь данных — 3 критичных сущности

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
