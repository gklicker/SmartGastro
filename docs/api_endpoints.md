# SmartGastro — Diseño de API REST

Diseño de endpoints para la segunda entrega del sistema, donde la aplicación de consola migrará a una arquitectura web con Flask y una API REST consumida desde el frontend.

---

## Convenciones

- **Base URL:** `https://api.smartgastro.com/api`
- **Formato:** JSON (`Content-Type: application/json`)
- **Autenticación:** Bearer Token (JWT) en el header `Authorization`
- **Códigos de respuesta:** `200 OK`, `201 Created`, `400 Bad Request`, `404 Not Found`, `409 Conflict`

---

## Módulo: Productos / Inventario

| Acción | Método | Endpoint | Body (JSON) | Respuesta exitosa |
|---|---|---|---|---|
| Registrar un nuevo producto | `POST` | `/productos` | `{"nombre": "Hamburguesa Doble", "precio": 5000, "stock": 20, "stock_minimo": 5}` | `201` — producto creado con `id` |
| Ver todos los productos | `GET` | `/productos` | — | `200` — lista de productos con stock actual |
| Ver un producto por ID | `GET` | `/productos/{id}` | — | `200` — detalle del producto |
| Actualizar precio o stock mínimo | `PATCH` | `/productos/{id}` | `{"precio": 5500, "stock_minimo": 3}` | `200` — producto actualizado |
| Eliminar un producto del inventario | `DELETE` | `/productos/{id}` | — | `200` — `{"mensaje": "Producto eliminado"}` |

---

## Módulo: Ventas

| Acción | Método | Endpoint | Body (JSON) | Respuesta exitosa |
|---|---|---|---|---|
| Registrar una venta | `POST` | `/ventas` | `{"evento_id": 1, "items": [{"producto_id": 3, "cantidad": 2}]}` | `201` — venta con total y stock actualizado |
| Ver historial de ventas | `GET` | `/ventas` | — | `200` — lista de ventas con detalle |
| Ver ventas de un evento | `GET` | `/ventas?evento_id={id}` | — | `200` — ventas filtradas por evento |

---

## Módulo: Eventos

| Acción | Método | Endpoint | Body (JSON) | Respuesta exitosa |
|---|---|---|---|---|
| Crear un evento | `POST` | `/eventos` | `{"nombre": "Feria Palermo", "ubicacion": "Palermo, CABA", "fecha": "2026-05-10", "latitud": -34.5855, "longitud": -58.4370}` | `201` — evento creado con pronóstico del clima incluido |
| Ver todos los eventos | `GET` | `/eventos` | — | `200` — lista de eventos con estado del clima |
| Ver pronóstico de un evento | `GET` | `/eventos/{id}/pronostico` | — | `200` — `{"estado": "Despejado", "lluvia_mm": 0.0, "temp_min": 14, "temp_max": 22}` |

---

## Módulo: Menú (2da entrega)

| Acción | Método | Endpoint | Body (JSON) | Respuesta exitosa |
|---|---|---|---|---|
| Agregar plato al menú | `POST` | `/menu` | `{"nombre": "Combo Clásico", "precio": 7500, "descripcion": "Hamburguesa + papas + bebida"}` | `201` — plato creado |
| Ver el menú completo | `GET` | `/menu` | — | `200` — lista de platos activos |
| Actualizar estado de un plato | `PATCH` | `/menu/{id}` | `{"activo": false}` | `200` — plato desactivado |

---

## Ejemplo de respuesta — `POST /ventas`

```json
{
  "id": 12,
  "evento": "Feria Palermo",
  "fecha": "2026-05-10T20:35:00",
  "items": [
    { "producto": "Hamburguesa Doble", "cantidad": 2, "precio_unitario": 5000, "subtotal": 10000 }
  ],
  "total": 10000,
  "stock_alertas": [
    { "producto": "Hamburguesa Doble", "stock_actual": 3, "stock_minimo": 5, "alerta": true }
  ]
}
```

## Ejemplo de respuesta — `GET /eventos/{id}/pronostico`

```json
{
  "evento_id": 1,
  "nombre": "Feria Palermo",
  "fecha": "2026-05-10",
  "pronostico": {
    "estado": "Lluvia leve — preparar mercadería reducida",
    "lluvia_total_mm": 2.4,
    "temp_min": 12.0,
    "temp_max": 18.5,
    "fuente": "Open-Meteo API"
  }
}
```
