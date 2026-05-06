# Primera entrega: "Análisis, Modelado y Lógica Core"

**Fecha límite:** Viernes 8 de Mayo del 2026, 18:00 hs.  
**Modalidad:** Grupos de hasta 2 personas.

---

## Contexto del proyecto

Ustedes son una consultora tecnológica contactada por una asociación de dueños de Foodtrucks. Actualmente gestionan sus ventas, inventario y ubicaciones en Excel o papel.

**Problemas principales:**
- Van a ferias al aire libre y si llueve, pierden toda la mercadería preparada.
- Se quedan sin stock a mitad del evento.

Se solicita diseñar **SmartGastro**: un sistema para gestionar inventario, ventas y ubicaciones.

**Objetivo:** Evaluar la captura de requerimientos (Agilidad), el análisis de negocio, el modelado del sistema (UML) y la base algorítmica mediante POO en consola.

> **Nota:** En la segunda entrega (final de cuatrimestre), el sistema pasará de la consola a la web usando Flask y APIs.

---

## Parte A: Negocio y gestión ágil

### 1. Propuesta laboral y rentabilidad
- **Propuesta de valor:** ¿Cómo le solucionará la vida al dueño del foodtruck?
- **Benchmarking:** Analizar al menos dos sistemas de gestión gastronómica existentes (ej. Maxirest, Fudo) y destacar el valor agregado de SmartGastro.
- **Rentabilidad:** Definir el modelo de monetización (ej. suscripción mensual, modelo freemium).

### 2. Gestión ágil
- Tablero Kanban (ej. Trello) con el estado de las tareas de esta entrega.
- Al menos 5 Historias de Usuario principales: `"Como [rol], quiero [acción] para [beneficio]"`.

---

## Parte B: Modelado y arquitectura (UML y datos)

### 1. Diagrama de Flujo de Datos (DFD)
- **Nivel 0 (Contexto):** Identificar entidades externas (ej. Cliente, Cocinero, API de Clima).
- **Nivel 1:** Mostrar los procesos principales del negocio (ej. `1.0 Gestionar Pedido`, `2.0 Controlar Stock`).

### 2. Modelo de datos
- Diagrama Entidad-Relación (DER) con cardinalidades (1:N, N:M).
- Diccionario de datos de las **3 entidades más críticas** (ej. Producto, Pedido, Cliente): nombre del campo, tipo de dato y descripción.

### 3. Trazabilidad y balanceo
Justificación breve que demuestre que todo flujo de datos del DFD impacta en una entidad del DER, y que ambos modelos responden a las Historias de Usuario de la Parte A.

---

## Parte C: Motor lógico (Prototipo en consola Python)

### 1. Código fuente
Script en Python puro implementando las clases del Diagrama de Clases (ej. `Foodtruck`, `Producto`, `Inventario`).

### 2. Interactividad
Menú iterativo (`while`) en terminal que permita:
- Agregar un producto al inventario.
- Registrar una venta (descontando stock).
- Mostrar el inventario actual.

### 3. Restricción técnica — encapsulamiento
El stock **no puede modificarse directamente** (`producto.stock = 10`). Debe hacerse a través de métodos (getters/setters) con validaciones lógicas (ej. error si se intenta vender con stock 0).

---

## Parte D: Diseño de integraciones (API REST)

Diseñar al menos **4 endpoints** fundamentales completando una matriz:

| Acción | Método HTTP | Endpoint | Body (JSON) |
|---|---|---|---|
| Registrar un nuevo plato | `POST` | `/api/productos` | `{"nombre": "Hamburguesa Doble", "precio": 5000, "stock": 20}` |
| Ver el menú completo | — | — | — |
| Actualizar estado de pedido a 'Listo' | — | — | — |
| Eliminar un producto del inventario | — | — | — |

---

## Formato de entrega

### 1. Archivo comprimido (.zip / .rar) → DavinciCampus

PDF con toda la documentación teórica (Partes A, B y D):

- **Carátula:** Materia, Docente, Nombre y Apellido de los integrantes, fecha de entrega.
- **Contenido:**
  - Metodología y negocio: Historias de Usuario (INVEST), capturas del tablero Kanban, Benchmarking/ROI.
  - Análisis y diseño: Diagrama de Contexto, DFD Nivel 1, DER, Diccionario de datos, Trazabilidad.
  - Diseño de APIs: Matriz con los 4 endpoints + captura de Postman con respuesta exitosa (ej. API de clima).
  - **Enlace al repositorio de GitHub** visible en la primera o segunda página.

### 2. Repositorio público en GitHub (Parte C)

- Archivo `.py` con el motor lógico (POO + encapsulamiento).
- `README.md` con descripción del proyecto, funcionalidades e instrucciones de ejecución.
- *(Opcional/Bonus)* Colección de Postman exportada en `.json`.

---

> **Atención:** La entrega oficial es por DavinciCampus. Solo ante caída del sistema se acepta envío por correo a **juan.stenico@davinci.edu.ar**, incluyendo siempre el enlace a GitHub en el cuerpo del correo.
