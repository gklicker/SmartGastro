from models.producto import Producto


class InventoryService:
    def __init__(self, producto_repo):
        self.__producto_repo = producto_repo

    def get_product(self, nombre):
        return self.__producto_repo.find_by_name(nombre)

    def add_product(self, nombre, precio, stock, stock_minimo=5):
        producto = Producto(nombre, precio, stock, stock_minimo)
        self.__producto_repo.add(producto)
        return producto

    def add_stock(self, nombre, cantidad):
        producto = self.__producto_repo.find_by_name(nombre)
        if not producto:
            raise ValueError(f"Producto '{nombre}' no encontrado.")
        producto.set_stock(producto.get_stock() + cantidad)
        return producto

    def show_inventory(self):
        productos = self.__producto_repo.get_all()
        if not productos:
            print("El inventario está vacío.")
            return
        print("\n--- Inventario ---")
        for producto in productos:
            print(f"  {producto}")

    def check_alerts(self):
        alertas = [p for p in self.__producto_repo.get_all() if p.has_low_stock()]
        if alertas:
            print("\nAlerta de stock bajo:")
            for p in alertas:
                print(f"  - {p.get_name()}: {p.get_stock()} unidades")
