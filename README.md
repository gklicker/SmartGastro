# SmartGastro

Sistema de gestión de inventario, ventas y ubicaciones para una red de Foodtrucks.

---

## Contexto académico

Trabajo parcial para la materia **Análisis y Metodología de Sistemas**  
Cuatrimestre **26-1** · Grupo **ACN4AP**

---

## Consigna

Una consultora tecnológica fue contactada por una asociación de dueños de Foodtrucks. Actualmente gestionan sus ventas, inventario y ubicaciones en Excel o en papel. Los problemas principales: pérdida de mercadería por mal clima en ferias al aire libre y quedarse sin stock a mitad de un evento.

Se solicita diseñar **SmartGastro**, un sistema para gestionar inventario, ventas y ubicaciones.

**Primera entrega (parcial):** aplicación de consola en Python con arquitectura orientada a objetos, captura de requerimientos, análisis de negocio y modelado UML.

**Segunda entrega (final):** migración a la web utilizando Flask y REST API.

---

## Funcionalidades

- Agregar productos al inventario con validación de duplicados
- Registrar ventas con descuento automático de stock
- Consultar el inventario actual con alertas de stock bajo
- Crear eventos con pronóstico del clima en tiempo real (Open-Meteo API)
- Ver historial de ventas por evento
- Gestionar usuarios con roles diferenciados (owner, accountant, seller, cashier, cook)
- Gestionar foodtrucks con inventario propio y staff asignado
- Crear recetas de platos del menú vinculadas a ingredientes con unidades
- Emitir y cerrar tickets de venta con descuento automático por receta
- Soporte de múltiples medios de pago: efectivo, tarjeta, MercadoPago
- Cancelar o reembolsar tickets en estados intermedios

---

## Modelos

| Modelo | Descripción |
|---|---|
| `Ingredient` | Ingrediente con nombre, unidad y alerta de stock mínimo |
| `Inventory` | Inventario de ingredientes por foodtruck; calcula porciones disponibles |
| `MenuItem` | Plato del menú con precio y lista de ingredientes (receta) |
| `Receipt` / `ReceiptItem` | Ticket de venta con ítems, medio de pago y estado (open / closed / cancelled / refunded) |
| `Foodtruck` | Foodtruck con inventario propio, staff y tickets de venta |
| `User` | Usuario con login, contraseña hasheada (SHA-256) y rol |
| `Role` | Enum de roles: owner, accountant, seller, cashier, cook |
| `Event` | Evento/feria con ubicación, fecha y pronóstico del clima |

---

## Arquitectura

```
cli.py              ← menú interactivo (consola)
services/           ← lógica de negocio y orquestación
  inventory_service.py
  sale_service.py
  event_service.py
  menu_service.py
  receipt_service.py
  foodtruck_service.py
  user_service.py
repository/
  in_memory/        ← almacenamiento en memoria (reemplazable por DB)
models/             ← clases con encapsulamiento estricto
  ingredient.py · inventory.py · menu_item.py
  receipt.py · foodtruck.py · user.py · role.py · event.py
migrations/         ← scripts de migración de base de datos (2da entrega)
external/           ← integración con API del clima
```

---

## Stack

| Tecnología | Uso |
|---|---|
| Python 3 | Lógica de negocio, consola (1ra entrega) |
| Flask | Backend web (2da entrega) |
| HTML / CSS / JS | Frontend (2da entrega) |

---

## Cómo ejecutar

**1. Crear el entorno virtual**
```bash
python3 -m venv .venv
```

**2. Activar el entorno**
```bash
# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

**3. Instalar dependencias**
```bash
pip install -r requirements.txt
```

**4. Ejecutar**
```bash
python3 cli.py
```
