class Inventario:
    def __init__(self):
        self.__productos = []

    def add_product(self, producto):
        self.__productos.append(producto)

    def find_product(self, nombre):
        for producto in self.__productos:
            if producto.get_name().lower() == nombre.lower():
                return producto
        return None

    def show_inventory(self):
        if not self.__productos:
            print("El inventario está vacío.")
            return
        print("\n--- Inventario ---")
        for producto in self.__productos:
            print(f"  {producto}")

    def check_alerts(self):
        alertas = [p for p in self.__productos if p.has_low_stock()]
        if alertas:
            print("\n⚠ Alerta de stock bajo:")
            for p in alertas:
                print(f"  - {p.get_name()}: {p.get_stock()} unidades")

    def get_products(self):
        return list(self.__productos)
