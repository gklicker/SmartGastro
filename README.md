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

## Stack

| Tecnología | Uso |
|---|---|
| Python 3 | Lógica de negocio, consola (1ra entrega) |
| Flask | Backend web (2da entrega) |
| HTML / CSS / JS | Frontend (2da entrega) |

---

## Funcionalidades

- Agregar productos al inventario
- Registrar ventas con descuento automático de stock
- Consultar el inventario actual con alertas de stock bajo
- Consultar el pronóstico del clima antes de un evento

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
