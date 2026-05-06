# Часть B.1 — Диаграмма потоков данных (DFD)

## Уровень 0 — Диаграмма контекста

**Система:** SmartGastro (один прямоугольник посередине)

**Внешние сущности:**
- **Владелец / Оператор** — управляет системой, регистрирует продажи и продукты
- **Cocinero** — консультирует инвентарь перед готовкой
- **API Погоды** — внешний сервис прогноза

**Потоки данных:**

| Откуда | Куда | Данные |
|---|---|---|
| Владелец | SmartGastro | Данные продуктов, регистрация продаж, запросы |
| SmartGastro | Владелец | Состояние инвентаря, алерты стока, история продаж, погодный алерт |
| Cocinero | SmartGastro | Запрос доступных ингредиентов |
| SmartGastro | Cocinero | Список доступных ингредиентов, алерт нехватки |
| API Погоды | SmartGastro | Метеопрогноз |

---

## Уровень 1 — Основные процессы

**Процессы:**
- `1.0 Gestionar Inventario` — добавление/обновление продуктов
- `2.0 Registrar Venta` — запись продажи, списание стока
- `3.0 Controlar Stock` — проверка минимумов, генерация алертов
- `4.0 Consultar Clima` — получение прогноза, генерация погодного алерта

**Хранилища данных:**
- `D1 Inventario` — продукты и остатки
- `D2 Ventas` — история продаж
- `D3 Eventos` — локации и события

**Потоки между процессами и хранилищами:**

| Процесс | Сущность / Хранилище | Направление | Данные |
|---|---|---|---|
| 1.0 | Владелец | ← | Nuevo producto, stock inicial |
| 1.0 | D1 | → | Producto registrado |
| 2.0 | Владелец | ← | Datos de venta |
| 2.0 | D1 | ← → | Consulta y descuenta stock |
| 2.0 | D2 | → | Registro de venta |
| 3.0 | D1 | ← | Stock actual |
| 3.0 | Владелец | → | Alerta de stock bajo |
| 3.0 | Cocinero | → | Alerta de ingrediente faltante |
| 4.0 | API Погоды | ← | Pronóstico meteorológico |
| 4.0 | D3 | ← | Ubicación del evento |
| 4.0 | Владелец | → | Alerta climática |
| — | Cocinero | → SmartGastro | Consulta de stock disponible |
| 1.0 | Cocinero | ← | Lista de ingredientes disponibles |
