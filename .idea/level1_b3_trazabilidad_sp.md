# Parte B.3 — Trazabilidad y balanceo

## Matriz de trazabilidad

| Historia de Usuario | Proceso DFD | Almacén DFD | Entidad DER |
|---|---|---|---|
| HU1: Agregar producto al inventario | 1.0 Gestionar Inventario | D1 Inventario | Producto |
| HU2: Registrar ventas y descontar stock | 2.0 Registrar Venta | D1 Inventario, D2 Ventas | Venta, DetalleVenta, Producto |
| HU3: Alerta de stock bajo | 3.0 Controlar Stock | D1 Inventario | Producto (campo stock_minimo) |
| HU4: Pronóstico del clima antes del evento | 4.0 Consultar Clima | D3 Eventos | Evento (campo pronostico_clima) |
| HU5: Historial de ventas por ubicación | 2.0 Registrar Venta | D2 Ventas, D3 Eventos | Venta, Evento (FK id_evento) |

## Justificación

Todas las Historias de Usuario trazabilidad a un proceso específico del DFD, el cual lee o escribe datos en un almacén representado como entidad en el DER. Ningún flujo de datos del DFD queda sin su entidad correspondiente, y ninguna entidad del DER fue incorporada sin respaldo en las Historias de Usuario.
