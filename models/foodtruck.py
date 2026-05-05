from models.inventario import Inventario


class Foodtruck:
    def __init__(self, nombre):
        self.__nombre = nombre
        self.__inventario = Inventario()
        self.__ventas = []

    def get_inventory(self):
        return self.__inventario

    def register_sale(self, venta):
        self.__ventas.append(venta)

    def show_inventory(self):
        self.__inventario.show_inventory()
        self.__inventario.check_alerts()

    def show_sales(self):
        if not self.__ventas:
            print("No hay ventas registradas.")
            return
        print(f"\n--- Ventas de {self.__nombre} ---")
        for venta in self.__ventas:
            print(venta)

    def __str__(self):
        return f"Foodtruck: {self.__nombre}"
