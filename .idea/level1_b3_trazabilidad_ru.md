# Часть B.3 — Трассируемость и балансировка

## Матрица трассируемости

| Historia de Usuario | Proceso DFD | Almacén DFD | Entidad DER |
|---|---|---|---|
| HU1: Добавить продукт в инвентарь | 1.0 Gestionar Inventario | D1 Inventario | Producto |
| HU2: Регистрировать продажи, списывать сток | 2.0 Registrar Venta | D1 Inventario, D2 Ventas | Venta, DetalleVenta, Producto |
| HU3: Алерт при низком стоке | 3.0 Controlar Stock | D1 Inventario | Producto (campo stock_minimo) |
| HU4: Прогноз погоды перед событием | 4.0 Consultar Clima | D3 Eventos | Evento (campo pronostico_clima) |
| HU5: История продаж по локациям | 2.0 Registrar Venta | D2 Ventas, D3 Eventos | Venta, Evento (FK id_evento) |

## Обоснование

Все пять Историй Пользователя трассируются к конкретному процессу DFD, который в свою очередь читает или записывает данные в хранилище, отражённое как сущность в DER. Ни один поток данных DFD не остаётся без соответствующей сущности, ни одна сущность DER не введена без обоснования в Историях Пользователя.
