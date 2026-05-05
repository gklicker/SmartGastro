from datetime import datetime


class Venta:
    _counter = 1

    def __init__(self, evento):
        self.__id_venta = Venta._counter
        Venta._counter += 1
        self.__fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.__evento = evento
        self.__detalles = []

    def add_item(self, detalle):
        self.__detalles.append(detalle)

    def calculate_total(self):
        return sum(d.get_subtotal() for d in self.__detalles)

    def get_id(self):
        return self.__id_venta

    def __str__(self):
        lineas = [
            f"\nVenta #{self.__id_venta} | {self.__fecha} | Evento: {self.__evento.get_name()}",
            "  Productos:"
        ]
        for detalle in self.__detalles:
            lineas.append(f"    {detalle}")
        lineas.append(f"  Total: ${self.calculate_total():.2f}")
        return "\n".join(lineas)
