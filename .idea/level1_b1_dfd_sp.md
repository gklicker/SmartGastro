# Parte B.1 — Diagrama de Flujo de Datos (DFD)

## Nivel 0 — Diagrama de Contexto

**Sistema:** SmartGastro (un rectángulo central)

**Entidades externas:**
- **Dueño / Operador** — gestiona el sistema, registra ventas y productos
- **Cocinero** — consulta el inventario antes de preparar los platos
- **API del Clima** — servicio externo de pronóstico meteorológico

**Flujos de datos:**

| Desde | Hacia | Datos |
|---|---|---|
| Dueño | SmartGastro | Datos de productos, registro de ventas, consultas |
| SmartGastro | Dueño | Estado del inventario, alertas de stock, historial de ventas, alerta climática |
| Cocinero | SmartGastro | Consulta de ingredientes disponibles |
| SmartGastro | Cocinero | Lista de ingredientes disponibles, alerta de faltante |
| API del Clima | SmartGastro | Pronóstico meteorológico |

---

## Nivel 1 — Procesos principales

**Procesos:**
- `1.0 Gestionar Inventario` — alta y actualización de productos
- `2.0 Registrar Venta` — registro de venta y descuento de stock
- `3.0 Controlar Stock` — verificación de mínimos y generación de alertas
- `4.0 Consultar Clima` — obtención del pronóstico y generación de alerta climática

**Almacenes de datos:**
- `D1 Inventario` — productos y cantidades disponibles
- `D2 Ventas` — historial de ventas
- `D3 Eventos` — ubicaciones y eventos registrados

**Flujos entre procesos y almacenes:**

| Proceso | Entidad / Almacén | Dirección | Datos |
|---|---|---|---|
| 1.0 | Dueño | ← | Nuevo producto, stock inicial |
| 1.0 | D1 | → | Producto registrado |
| 1.0 | Cocinero | → | Lista de ingredientes disponibles |
| 2.0 | Dueño | ← | Datos de venta |
| 2.0 | D1 | ← → | Consulta y descuenta stock |
| 2.0 | D2 | → | Registro de venta |
| 3.0 | D1 | ← | Stock actual |
| 3.0 | Dueño | → | Alerta de stock bajo |
| 3.0 | Cocinero | → | Alerta de ingrediente faltante |
| 4.0 | API del Clima | ← | Pronóstico meteorológico |
| 4.0 | D3 | ← | Ubicación del evento |
| 4.0 | Dueño | → | Alerta climática |
| — | Cocinero | → SmartGastro | Consulta de stock disponible |
