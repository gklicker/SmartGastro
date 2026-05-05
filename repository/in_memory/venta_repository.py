class VentaRepository:
    def __init__(self):
        self.__ventas = []

    def add(self, venta):
        self.__ventas.append(venta)

    def get_all(self):
        return list(self.__ventas)

    def find_by_id(self, id_venta):
        for venta in self.__ventas:
            if venta.get_id() == id_venta:
                return venta
        return None
