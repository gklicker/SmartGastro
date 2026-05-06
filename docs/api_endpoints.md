# SmartGastro — Diseño de API REST

Diseño de endpoints para la segunda entrega del sistema, donde la aplicación de consola migrará a una arquitectura web con Flask y una API REST consumida desde el frontend.

---

## Convenciones

- **Base URL:** `https://api.smartgastro.com/api`
- **Formato:** JSON (`Content-Type: application/json`)
- **Autenticación:** Bearer Token (JWT) en el header `Authorization`
- **Códigos de respuesta:** `200 OK`, `201 Created`, `204 No Content`, `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `409 Conflict`

---

## Módulo: Autenticación

| Acción | Método | Endpoint | Body (JSON) | Respuesta exitosa |
|---|---|---|---|---|
| Iniciar sesión | `POST` | `/auth/login` | `{"login": "jperez", "password": "abc123"}` | `200` — `{"token": "<jwt>", "rol": "cashier", "nombre": "Juan Pérez"}` |
| Cerrar sesión | `POST` | `/auth/logout` | — | `204` |

---

## Módulo: Usuarios

> Roles disponibles: `owner`, `accountant`, `seller`, `cashier`, `cook`

| Acción | Método | Endpoint | Body (JSON) | Respuesta exitosa |
|---|---|---|---|---|
| Crear usuario | `POST` | `/usuarios` | `{"login": "mgarcia", "password": "xyz789", "full_name": "María García", "role": "cashier"}` | `201` — usuario creado con `id` |
| Ver todos los usuarios | `GET` | `/usuarios` | — | `200` — lista de usuarios (sin password) |
| Ver usuario por ID | `GET` | `/usuarios/{id}` | — | `200` — detalle del usuario |
| Desactivar usuario | `PATCH` | `/usuarios/{id}/desactivar` | — | `200` — `{"activo": false}` |
| Eliminar usuario | `DELETE` | `/usuarios/{id}` | — | `204` |

---

## Módulo: Foodtrucks

| Acción | Método | Endpoint | Body (JSON) | Respuesta exitosa |
|---|---|---|---|---|
| Registrar foodtruck | `POST` | `/foodtrucks` | `{"nombre": "El Rincón", "patente": "AB123CD", "descripcion": "Hamburguesas artesanales"}` | `201` — foodtruck creado con `id` |
| Ver todos los foodtrucks | `GET` | `/foodtrucks` | — | `200` — lista con estado activo/inactivo |
| Ver foodtruck por ID | `GET` | `/foodtrucks/{id}` | — | `200` — detalle con staff e inventario |
| Asignar empleado | `POST` | `/foodtrucks/{id}/staff` | `{"usuario_id": 3}` | `200` — staff actualizado |
| Desactivar foodtruck | `PATCH` | `/foodtrucks/{id}/desactivar` | — | `200` — `{"activo": false}` |
| Eliminar foodtruck | `DELETE` | `/foodtrucks/{id}` | — | `204` |

---

## Módulo: Ingredientes

| Acción | Método | Endpoint | Body (JSON) | Respuesta exitosa |
|---|---|---|---|---|
| Registrar ingrediente | `POST` | `/ingredientes` | `{"nombre": "Carne vacuna", "unidad": "kg", "stock_minimo_alerta": 2}` | `201` — ingrediente creado con `id` |
| Ver todos los ingredientes | `GET` | `/ingredientes` | — | `200` — lista con unidades |
| Ver ingrediente por ID | `GET` | `/ingredientes/{id}` | — | `200` — detalle del ingrediente |
| Eliminar ingrediente | `DELETE` | `/ingredientes/{id}` | — | `204` |

---

## Módulo: Inventario

| Acción | Método | Endpoint | Body (JSON) | Respuesta exitosa |
|---|---|---|---|---|
| Ver inventario de un foodtruck | `GET` | `/foodtrucks/{id}/inventario` | — | `200` — stock por ingrediente con alertas |
| Agregar stock | `POST` | `/foodtrucks/{id}/inventario` | `{"ingrediente_id": 2, "cantidad": 10}` | `200` — stock actualizado |
| Ver alertas de stock bajo | `GET` | `/foodtrucks/{id}/inventario/alertas` | — | `200` — ingredientes por debajo del mínimo |

---

## Módulo: Menú

| Acción | Método | Endpoint | Body (JSON) | Respuesta exitosa |
|---|---|---|---|---|
| Crear plato | `POST` | `/menu` | `{"nombre": "Combo Clásico", "precio": 7500, "descripcion": "Hamburguesa + papas + bebida"}` | `201` — plato creado con `id` |
| Agregar ingrediente a un plato | `POST` | `/menu/{id}/ingredientes` | `{"ingrediente_id": 2, "cantidad": 0.2}` | `200` — receta actualizada |
| Ver menú completo | `GET` | `/menu` | — | `200` — lista de platos activos con receta |
| Ver plato por ID | `GET` | `/menu/{id}` | — | `200` — detalle con ingredientes y porciones disponibles |
| Actualizar precio | `PATCH` | `/menu/{id}` | `{"precio": 8000}` | `200` — plato actualizado |
| Desactivar plato | `PATCH` | `/menu/{id}/desactivar` | — | `200` — `{"activo": false}` |
| Eliminar plato | `DELETE` | `/menu/{id}` | — | `204` |

---

## Módulo: Eventos

| Acción | Método | Endpoint | Body (JSON) | Respuesta exitosa |
|---|---|---|---|---|
| Crear evento | `POST` | `/eventos` | `{"nombre": "Feria Palermo", "localidad": "Buenos Aires", "fecha_inicio": "2026-05-10T18:00:00", "fecha_fin": "2026-05-10T23:00:00", "creado_por": 1}` | `201` — evento con pronóstico del clima incluido |
| Ver todos los eventos | `GET` | `/eventos` | — | `200` — lista con estado y clima |
| Ver evento por ID | `GET` | `/eventos/{id}` | — | `200` — detalle completo |
| Iniciar evento | `PATCH` | `/eventos/{id}/iniciar` | — | `200` — `{"estado": "ongoing"}` |
| Completar evento | `PATCH` | `/eventos/{id}/completar` | — | `200` — `{"estado": "completed"}` |
| Cancelar evento | `PATCH` | `/eventos/{id}/cancelar` | `{"motivo": "Lluvia intensa", "comentario": "Pronóstico desfavorable"}` | `200` — `{"estado": "cancelled"}` |
| Ver pronóstico del clima | `GET` | `/eventos/{id}/pronostico` | — | `200` — estado del clima con lluvia y temperatura |

---

## Módulo: Tickets (Receipts)

| Acción | Método | Endpoint | Body (JSON) | Respuesta exitosa |
|---|---|---|---|---|
| Abrir ticket | `POST` | `/tickets` | `{"foodtruck_id": 1, "cajero_id": 3, "medio_pago": "mercadopago", "evento_id": 2}` | `201` — ticket abierto con `id` |
| Agregar ítem al ticket | `POST` | `/tickets/{id}/items` | `{"menu_item_id": 5, "cantidad": 2}` | `200` — ticket con total actualizado |
| Ver ticket | `GET` | `/tickets/{id}` | — | `200` — detalle con ítems y total |
| Cerrar ticket | `PATCH` | `/tickets/{id}/cerrar` | — | `200` — ticket cerrado, stock descontado automáticamente |
| Cancelar ticket | `PATCH` | `/tickets/{id}/cancelar` | — | `200` — `{"estado": "cancelled"}` |
| Ver tickets de un evento | `GET` | `/tickets?evento_id={id}` | — | `200` — lista de tickets filtrada |

> Medios de pago disponibles: `cash`, `card`, `mercadopago`

---

## Ejemplos de respuesta

### `POST /eventos` — evento creado con pronóstico

```json
{
  "id": 4,
  "nombre": "Feria Palermo",
  "localidad": "Buenos Aires, Argentina",
  "fecha_inicio": "2026-05-10T18:00:00",
  "fecha_fin": "2026-05-10T23:00:00",
  "estado": "planned",
  "pronostico": {
    "estado": "Lluvia leve — preparar mercadería reducida",
    "lluvia_total_mm": 2.4,
    "temp_min": 12.0,
    "temp_max": 18.5,
    "fuente": "Open-Meteo API"
  }
}
```

### `PATCH /tickets/{id}/cerrar` — ticket cerrado con stock descontado

```json
{
  "id": 12,
  "estado": "closed",
  "medio_pago": "mercadopago",
  "cerrado_at": "2026-05-10T21:42:00",
  "items": [
    { "plato": "Combo Clásico", "cantidad": 2, "precio_unitario": 7500, "subtotal": 15000 }
  ],
  "total": 15000,
  "alertas_stock": [
    { "ingrediente": "Carne vacuna", "stock_actual": 1.4, "stock_minimo": 2.0, "alerta": true }
  ]
}
```

### `GET /foodtrucks/{id}/inventario/alertas`

```json
{
  "foodtruck_id": 1,
  "alertas": [
    { "ingrediente_id": 2, "nombre": "Carne vacuna", "unidad": "kg", "stock_actual": 1.4, "stock_minimo": 2.0 },
    { "ingrediente_id": 5, "nombre": "Pan brioche", "unidad": "unidades", "stock_actual": 4, "stock_minimo": 10 }
  ]
}
```
