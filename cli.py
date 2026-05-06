from external.weather import geocode
from repository.in_memory.product_repository import ProductRepository
from repository.in_memory.receipt_repository import ReceiptRepository
from repository.in_memory.event_repository import EventRepository
from services.inventory_service import InventoryService
from services.sale_service import SaleService

product_repo = ProductRepository()
receipt_repo = ReceiptRepository()
event_repo = EventRepository()

inventory = InventoryService(product_repo)
sales = SaleService(product_repo, receipt_repo, event_repo)


def menu_agregar_producto():
    print("\n--- Agregar producto ---")
    nombre = input("Nombre: ").strip()
    precio = float(input("Precio: "))

    existente = inventory.get_product(nombre)
    if existente:
        if existente.get_price() == precio:
            confirmar = (
                input(
                    f"'{nombre}' ya existe (stock actual: {existente.get_stock()}). "
                    f"¿Querés agregar stock? (s/n): "
                )
                .strip()
                .lower()
            )
            if confirmar == "s":
                cantidad = int(input("Cantidad a agregar: "))
                producto = inventory.add_stock(nombre, cantidad)
                print(f"✓ Stock actualizado: {producto}")
            else:
                print("✗ Operación cancelada.")
        else:
            print(
                f"✗ '{nombre}' ya existe con un precio diferente (${existente.get_price():.2f})."
            )
        return

    stock = int(input("Stock inicial: "))
    stock_minimo = input("Stock mínimo (Enter para 5): ").strip()
    stock_minimo = int(stock_minimo) if stock_minimo else 5
    producto = inventory.add_product(nombre, precio, stock, stock_minimo)
    print(f"✓ Producto agregado: {producto}")


def menu_registrar_venta():
    print("\n--- Registrar venta ---")
    eventos = event_repo.get_all()
    if not eventos:
        print("✗ No hay eventos registrados. Creá un evento primero.")
        return
    print("Eventos disponibles:")
    for e in eventos:
        print(f"  - {e.get_name()}")
    nombre_evento = input("Nombre del evento: ").strip()

    items = []
    print("Ingresá los productos vendidos (Enter sin nombre para terminar):")
    while True:
        nombre_producto = input("  Producto: ").strip()
        if not nombre_producto:
            break
        cantidad = int(input("  Cantidad: "))
        items.append((nombre_producto, cantidad))

    if not items:
        print("✗ No se ingresaron productos.")
        return

    try:
        venta = sales.register_sale(nombre_evento, items)
        print(f"✓ Venta registrada:{venta}")
        inventory.check_alerts()
    except ValueError as e:
        print(f"✗ Error: {e}")


def menu_crear_evento():
    print("\n--- Crear evento ---")
    nombre = input("Nombre del evento: ").strip()
    fecha = input("Fecha (YYYY-MM-DD): ").strip()
    localidad = input("Localidad (ej: Palermo, Buenos Aires): ").strip()
    try:
        latitud, longitud, nombre_lugar, pais = geocode(localidad)
        print(f"  ✓ Localidad encontrada: {nombre_lugar}, {pais} ({latitud}, {longitud})")
        sales.create_event(nombre, f"{nombre_lugar}, {pais}", fecha, latitud, longitud)
    except ValueError as e:
        print(f"✗ {e}")
    except Exception as e:
        print(f"✗ Error al obtener el clima: {e}")


def main():
    print("=" * 40)
    print("       Bienvenido a SmartGastro")
    print("=" * 40)

    while True:
        print("\n¿Qué querés hacer?")
        print("  1. Agregar producto al inventario")
        print("  2. Registrar una venta")
        print("  3. Ver inventario")
        print("  4. Crear evento")
        print("  5. Ver historial de ventas")
        print("  0. Salir")

        opcion = input("\nOpción: ").strip()

        if opcion == "1":
            menu_agregar_producto()
        elif opcion == "2":
            menu_registrar_venta()
        elif opcion == "3":
            inventory.show_inventory()
            inventory.check_alerts()
        elif opcion == "4":
            menu_crear_evento()
        elif opcion == "5":
            sales.show_sales()
        elif opcion == "0":
            print("¡Hasta luego!")
            break
        else:
            print("✗ Opción inválida.")


if __name__ == "__main__":
    main()
