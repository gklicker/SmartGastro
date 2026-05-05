class ProductoRepository:
    def __init__(self):
        self.__productos = []

    def add(self, producto):
        self.__productos.append(producto)

    def find_by_name(self, nombre):
        for producto in self.__productos:
            if producto.get_name().lower() == nombre.lower():
                return producto
        return None

    def get_all(self):
        return list(self.__productos)

    def exists(self, nombre):
        return self.find_by_name(nombre) is not None
