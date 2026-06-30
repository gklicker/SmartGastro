# SmartGastro — Matriz de API y rutas web

## Contrato implementado en la entrega actual

Esta tabla documenta el comportamiento real de `app.py`. Las rutas de
formularios responden con una redirección `302` después de una operación para
evitar el reenvío del formulario al actualizar la página. La venta es la
operación REST asíncrona consumida por `fetch()`.

| Operación | Método | Ruta | Éxito | Casos límite |
|---|---|---|---|---|
| Ver login | `GET` | `/login` | `200 OK` | — |
| Iniciar sesión | `POST` | `/login` | `302 Found` hacia dashboard | `200 OK` mostrando error si las credenciales son inválidas |
| Cerrar sesión | `GET` | `/logout` | `302 Found` hacia login | — |
| Ver dashboard | `GET` | `/` | `200 OK` | `302 Found` si no hay sesión |
| Ver inventario | `GET` | `/ingredients` | `200 OK` | `302 Found` si no hay sesión |
| Crear ingrediente | `POST` | `/ingredients` | `302 Found` | `302 Found` con mensaje si hay datos inválidos o duplicados |
| Editar ingrediente | `POST` | `/ingredients/{id}/edit` | `302 Found` | `404 Not Found` si no existe |
| Registrar ingreso | `POST` | `/ingredients/{id}/receive` | `302 Found` | `302 Found` con error si la cantidad no es positiva; `404` si no existe |
| Eliminar ingrediente | `POST` | `/ingredients/{id}/delete` | `302 Found` | `404 Not Found` si no existe |
| Ver menú | `GET` | `/menu` | `200 OK` | `302 Found` si no hay sesión |
| Crear plato y receta | `POST` | `/menu` | `302 Found` | `302 Found` con error si precio o receta son inválidos |
| Editar o desactivar plato | `POST` | `/menu/{id}/edit` | `302 Found` | `404 Not Found` si no existe |
| Editar receta | `GET`, `POST` | `/menu/{id}/recipe` | `200 OK` / `302 Found` | `404` si no existe; `200` con error si la receta es inválida |
| Eliminar plato | `POST` | `/menu/{id}/delete` | `302 Found` | `302 Found` con error si tiene ventas; `404` si no existe |
| Ver ventas | `GET` | `/sales` | `200 OK` | `302 Found` si no hay sesión |
| Registrar venta | `POST` JSON | `/api/sales` | `201 Created` | `400 Bad Request` por JSON, cantidad, receta o stock; `500 Internal Server Error` por persistencia; `302 Found` si no hay sesión |

### Contrato de `POST /api/sales`

Body:

```json
{
  "items": [
    {"menu_item_id": 1, "quantity": 2},
    {"menu_item_id": 4, "quantity": 1}
  ],
  "payment_method": "card"
}
```

Respuestas:

- `201 Created`: venta registrada, total calculado y stock descontado.
- `400 Bad Request`: ticket vacío, cantidad inválida, plato inactivo, receta
  inexistente o stock insuficiente.
- `500 Internal Server Error`: error de base de datos; la transacción se
  revierte con `rollback`.
- `302 Found`: usuario no autenticado; se redirige al login.

La desactivación de un plato se realiza actualmente mediante
`POST /menu/{id}/edit`: si la operación es válida devuelve `302 Found` hacia el
menú. El `200 OK` indicado en el diseño REST de abajo corresponde al contrato
futuro de `PATCH /api/v1/menu/{id}/desactivar`, no a la ruta web actual.

---

## Diseño REST propuesto para evolución a producción

Diseño de endpoints para la segunda entrega del sistema, donde la aplicación de consola migrará a una arquitectura web con Flask y una API REST consumida desde el frontend.

---

## Convenciones globales

### Base URL y versioning
```
https://api.smartgastro.com/api/v1
```
El segmento `/v1` es obligatorio. Cambios que rompan compatibilidad (breaking changes) se publicarán en `/v2` sin dar de baja `/v1` hasta deprecación formal.

### Formato y fechas
- **Content-Type:** `application/json`
- **Autenticación:** `Authorization: Bearer <jwt>`
- **Fechas:** ISO 8601 UTC — `2026-05-10T21:00:00Z`
- **IDs:** enteros positivos

### Paginación (todos los endpoints GET de colecciones)

| Parámetro | Tipo | Default | Descripción |
|---|---|---|---|
| `page` | int | `1` | Número de página |
| `limit` | int | `20` | Resultados por página (máx. 100) |
| `sort` | string | varía | Campo de ordenamiento (ej. `nombre`, `fecha_inicio`) |
| `order` | `asc`\|`desc` | `asc` | Dirección del ordenamiento |

**Ejemplo:** `GET /api/v1/tickets?page=2&limit=10&sort=created_at&order=desc`

**Envelope de respuesta paginada:**
```json
{
  "data": [ ... ],
  "meta": {
    "page": 2,
    "limit": 10,
    "total": 87,
    "total_pages": 9
  }
}
```

### Formato de errores

Todas las respuestas de error siguen el mismo schema:

```json
{
  "error": "Unprocessable Entity",
  "message": "El campo 'precio' debe ser un número positivo",
  "code": 4221,
  "details": {
    "precio": ["debe ser mayor a 0"]
  }
}
```

| HTTP | `error` | Cuándo usarlo |
|---|---|---|
| `400` | Bad Request | Body malformado o tipo de dato incorrecto |
| `401` | Unauthorized | Token ausente o expirado |
| `403` | Forbidden | Token válido pero sin el rol requerido |
| `404` | Not Found | Recurso no encontrado |
| `409` | Conflict | Duplicado (ej. login ya existe) |
| `422` | Unprocessable Entity | Datos válidos pero con error de negocio (ej. precio negativo) |

### Roles y RBAC

Los roles disponibles son: `owner`, `accountant`, `cashier`, `seller`, `cook`.  
Cada endpoint indica el rol mínimo requerido con el símbolo 🔒.

| Símbolo | Significado |
|---|---|
| 🔒 `owner` | Solo dueños |
| 🔒 `owner, accountant` | Dueños o contadores |
| 🔒 `any` | Cualquier usuario autenticado |

### Soft Delete vs Hard Delete

- **Soft delete** (`PATCH .../desactivar`): marca el registro como inactivo (`activo: false`). El registro se conserva en la base de datos para mantener integridad referencial. Usado para usuarios, foodtrucks y platos del menú.
- **Hard delete** (`DELETE`): eliminación física. Solo permitida cuando el registro no tiene dependencias (ej. un ingrediente que nunca se usó en una receta). Si existen dependencias, la API devuelve `409 Conflict`.

---

## Módulo: Autenticación

| Acción | Método | Endpoint | Body | Respuesta | 🔒 Rol |
|---|---|---|---|---|---|
| Iniciar sesión | `POST` | `/auth/login` | `{"login": "jperez", "password": "abc123"}` | `200` — `{"token": "<jwt>", "rol": "cashier", "nombre": "Juan Pérez", "expires_at": "2026-05-11T21:00:00Z"}` | — |
| Cerrar sesión | `POST` | `/auth/logout` | — | `204` | `any` |

---

## Módulo: Usuarios

**Filtros disponibles:** `?rol=cashier`, `?activo=true`, `?nombre=garcia`

| Acción | Método | Endpoint | Body | Respuesta | 🔒 Rol |
|---|---|---|---|---|---|
| Crear usuario | `POST` | `/usuarios` | `{"login": "mgarcia", "password": "xyz789", "full_name": "María García", "role": "cashier"}` | `201` — usuario con `id` (sin `password`) | `owner` |
| Ver todos los usuarios | `GET` | `/usuarios` | — | `200` — lista paginada | `owner, accountant` |
| Ver usuario por ID | `GET` | `/usuarios/{id}` | — | `200` — detalle del usuario | `owner, accountant` |
| Actualizar usuario | `PATCH` | `/usuarios/{id}` | `{"full_name": "María García Ruiz", "role": "seller"}` | `200` — usuario actualizado | `owner` |
| Desactivar usuario | `PATCH` | `/usuarios/{id}/desactivar` | — | `200` — `{"activo": false}` *(soft delete)* | `owner` |
| Eliminar usuario | `DELETE` | `/usuarios/{id}` | — | `204` *(hard delete — falla con `409` si tiene tickets)* | `owner` |

---

## Módulo: Foodtrucks

**Filtros disponibles:** `?activo=true`, `?nombre=rincon`

| Acción | Método | Endpoint | Body | Respuesta | 🔒 Rol |
|---|---|---|---|---|---|
| Registrar foodtruck | `POST` | `/foodtrucks` | `{"nombre": "El Rincón", "patente": "AB123CD", "descripcion": "Hamburguesas artesanales"}` | `201` — foodtruck con `id` | `owner` |
| Ver todos los foodtrucks | `GET` | `/foodtrucks` | — | `200` — lista paginada con estado | `owner, accountant` |
| Ver foodtruck por ID | `GET` | `/foodtrucks/{id}` | — | `200` — detalle con staff e inventario | `any` |
| Actualizar foodtruck | `PATCH` | `/foodtrucks/{id}` | `{"nombre": "El Rincón 2", "patente": "XY456ZA", "descripcion": "..."}` | `200` — foodtruck actualizado | `owner` |
| Asignar empleado | `POST` | `/foodtrucks/{id}/staff` | `{"usuario_id": 3}` | `200` — staff actualizado | `owner` |
| Remover empleado | `DELETE` | `/foodtrucks/{id}/staff/{usuario_id}` | — | `204` | `owner` |
| Desactivar foodtruck | `PATCH` | `/foodtrucks/{id}/desactivar` | — | `200` — `{"activo": false}` *(soft delete)* | `owner` |
| Eliminar foodtruck | `DELETE` | `/foodtrucks/{id}` | — | `204` *(hard delete — falla con `409` si tiene tickets)* | `owner` |

---

## Módulo: Ingredientes

**Filtros disponibles:** `?nombre=carne`, `?unidad=kg`

| Acción | Método | Endpoint | Body | Respuesta | 🔒 Rol |
|---|---|---|---|---|---|
| Registrar ingrediente | `POST` | `/ingredientes` | `{"nombre": "Carne vacuna", "unidad": "kg", "stock_minimo_alerta": 2}` | `201` — ingrediente con `id` | `owner, cook` |
| Ver todos los ingredientes | `GET` | `/ingredientes` | — | `200` — lista paginada | `any` |
| Ver ingrediente por ID | `GET` | `/ingredientes/{id}` | — | `200` — detalle | `any` |
| Actualizar ingrediente | `PATCH` | `/ingredientes/{id}` | `{"stock_minimo_alerta": 3}` | `200` — ingrediente actualizado | `owner, cook` |
| Eliminar ingrediente | `DELETE` | `/ingredientes/{id}` | — | `204` *(hard delete — falla con `409` si está en alguna receta)* | `owner` |

---

## Módulo: Inventario

**Filtros disponibles:** `?alerta=true` (solo ingredientes bajo el mínimo)

| Acción | Método | Endpoint | Body | Respuesta | 🔒 Rol |
|---|---|---|---|---|---|
| Ver inventario de un foodtruck | `GET` | `/foodtrucks/{id}/inventario` | — | `200` — stock por ingrediente con alertas | `any` |
| Agregar stock | `POST` | `/foodtrucks/{id}/inventario` | `{"ingrediente_id": 2, "cantidad": 10}` | `200` — stock actualizado | `owner, cook` |
| Ver alertas de stock bajo | `GET` | `/foodtrucks/{id}/inventario/alertas` | — | `200` — solo ingredientes bajo el mínimo | `any` |

---

## Módulo: Menú

**Filtros disponibles:** `?activo=true`, `?nombre=combo`, `?precio_max=8000`

| Acción | Método | Endpoint | Body | Respuesta | 🔒 Rol |
|---|---|---|---|---|---|
| Crear plato | `POST` | `/menu` | `{"nombre": "Combo Clásico", "precio": 7500, "descripcion": "Hamburguesa + papas + bebida"}` | `201` — plato con `id` | `owner, cook` |
| Ver menú completo | `GET` | `/menu` | — | `200` — lista paginada de platos activos con receta | `any` |
| Ver plato por ID | `GET` | `/menu/{id}` | — | `200` — detalle con ingredientes y porciones disponibles | `any` |
| Actualizar plato | `PATCH` | `/menu/{id}` | `{"nombre": "Combo Clásico XL", "precio": 8500, "descripcion": "..."}` | `200` — plato actualizado | `owner, cook` |
| Agregar ingrediente a receta | `POST` | `/menu/{id}/ingredientes` | `{"ingrediente_id": 2, "cantidad": 0.2}` | `200` — receta actualizada | `owner, cook` |
| Remover ingrediente de receta | `DELETE` | `/menu/{id}/ingredientes/{ingrediente_id}` | — | `204` | `owner, cook` |
| Desactivar plato | `PATCH` | `/menu/{id}/desactivar` | — | `200` — `{"activo": false}` *(soft delete)* | `owner` |
| Eliminar plato | `DELETE` | `/menu/{id}` | — | `204` *(hard delete — falla con `409` si tiene tickets cerrados)* | `owner` |

---

## Módulo: Eventos

**Filtros disponibles:** `?estado=planned`, `?fecha_desde=2026-05-01T00:00:00Z&fecha_hasta=2026-05-31T23:59:59Z`

| Acción | Método | Endpoint | Body | Respuesta | 🔒 Rol |
|---|---|---|---|---|---|
| Crear evento | `POST` | `/eventos` | `{"nombre": "Feria Palermo", "localidad": "Buenos Aires", "fecha_inicio": "2026-05-10T18:00:00Z", "fecha_fin": "2026-05-10T23:00:00Z", "creado_por": 1}` | `201` — evento con pronóstico del clima | `owner, seller` |
| Ver todos los eventos | `GET` | `/eventos` | — | `200` — lista paginada con estado y clima | `any` |
| Ver evento por ID | `GET` | `/eventos/{id}` | — | `200` — detalle completo | `any` |
| Actualizar evento | `PATCH` | `/eventos/{id}` | `{"nombre": "Feria Palermo 2026", "fecha_fin": "2026-05-11T00:00:00Z"}` | `200` — solo si estado es `planned` | `owner, seller` |
| Iniciar evento | `PATCH` | `/eventos/{id}/iniciar` | — | `200` — `{"estado": "ongoing"}` | `owner, seller` |
| Completar evento | `PATCH` | `/eventos/{id}/completar` | — | `200` — `{"estado": "completed"}` | `owner, seller` |
| Cancelar evento | `PATCH` | `/eventos/{id}/cancelar` | `{"motivo": "Lluvia intensa", "comentario": "Pronóstico desfavorable"}` | `200` — `{"estado": "cancelled"}` | `owner` |
| Ver pronóstico del clima | `GET` | `/eventos/{id}/pronostico` | — | `200` — estado del clima con lluvia y temperatura | `any` |

---

## Módulo: Tickets (Receipts)

**Filtros disponibles:** `?evento_id=2`, `?estado=open`, `?cajero_id=3`, `?fecha_desde=2026-05-10T00:00:00Z&fecha_hasta=2026-05-10T23:59:59Z`

| Acción | Método | Endpoint | Body | Respuesta | 🔒 Rol |
|---|---|---|---|---|---|
| Abrir ticket | `POST` | `/tickets` | `{"foodtruck_id": 1, "cajero_id": 3, "medio_pago": "mercadopago", "evento_id": 2}` | `201` — ticket abierto con `id` | `cashier, seller` |
| Agregar ítem | `POST` | `/tickets/{id}/items` | `{"menu_item_id": 5, "cantidad": 2}` | `200` — ticket con total actualizado | `cashier, seller` |
| Agregar ítems en lote | `POST` | `/tickets/{id}/items/batch` | `{"items": [{"menu_item_id": 5, "cantidad": 2}, {"menu_item_id": 3, "cantidad": 1}]}` | `200` — ticket con todos los ítems y total | `cashier, seller` |
| Ver ticket | `GET` | `/tickets/{id}` | — | `200` — detalle con ítems y total | `any` |
| Ver todos los tickets | `GET` | `/tickets` | — | `200` — lista paginada | `owner, accountant` |
| Cerrar ticket | `PATCH` | `/tickets/{id}/cerrar` | — | `200` — ticket cerrado, stock descontado automáticamente | `cashier, seller` |
| Cancelar ticket | `PATCH` | `/tickets/{id}/cancelar` | — | `200` — `{"estado": "cancelled"}` | `cashier, owner` |

> Medios de pago disponibles: `cash`, `card`, `mercadopago`  
> Estados del ticket: `open` → `closed` | `open` → `cancelled`

---

## Ejemplos de respuesta

### `POST /api/v1/eventos` — evento creado con pronóstico

```json
{
  "id": 4,
  "nombre": "Feria Palermo",
  "localidad": "Buenos Aires, Argentina",
  "fecha_inicio": "2026-05-10T18:00:00Z",
  "fecha_fin": "2026-05-10T23:00:00Z",
  "estado": "planned",
  "creado_por": 1,
  "pronostico": {
    "estado": "Lluvia leve — preparar mercadería reducida",
    "lluvia_total_mm": 2.4,
    "temp_min": 12.0,
    "temp_max": 18.5,
    "fuente": "Open-Meteo API"
  }
}
```

### `PATCH /api/v1/tickets/{id}/cerrar` — ticket cerrado con alertas de stock

```json
{
  "id": 12,
  "estado": "closed",
  "medio_pago": "mercadopago",
  "created_at": "2026-05-10T21:35:00Z",
  "closed_at": "2026-05-10T21:42:00Z",
  "items": [
    { "plato": "Combo Clásico", "cantidad": 2, "precio_unitario": 7500, "subtotal": 15000 }
  ],
  "total": 15000,
  "alertas_stock": [
    { "ingrediente": "Carne vacuna", "unidad": "kg", "stock_actual": 1.4, "stock_minimo": 2.0 }
  ]
}
```

### `GET /api/v1/foodtrucks/{id}/inventario/alertas`

```json
{
  "foodtruck_id": 1,
  "alertas": [
    { "ingrediente_id": 2, "nombre": "Carne vacuna", "unidad": "kg", "stock_actual": 1.4, "stock_minimo": 2.0 },
    { "ingrediente_id": 5, "nombre": "Pan brioche", "unidad": "unidades", "stock_actual": 4, "stock_minimo": 10 }
  ]
}
```

### Error `422` — campo inválido

```json
{
  "error": "Unprocessable Entity",
  "message": "El campo 'precio' debe ser un número positivo",
  "code": 4221,
  "details": {
    "precio": ["debe ser mayor a 0"]
  }
}
```

### Error `409` — hard delete con dependencias

```json
{
  "error": "Conflict",
  "message": "No se puede eliminar el usuario: tiene 14 tickets cerrados asociados. Use PATCH /desactivar en su lugar.",
  "code": 4091
}
```
