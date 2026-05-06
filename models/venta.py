from datetime import datetime


class Venta:
    _counter = 1

    def __init__(self, evento, foodtruck=None, metodo_pago=None, empleado=None):
        self.__id_venta = Venta._counter
        Venta._counter += 1
        self.__fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.__evento = evento
        self.__foodtruck = foodtruck
        self.__metodo_pago = metodo_pago
        self.__empleado = empleado
        self.__detalles = []
        self.__anulado = False

    def add_item(self, detalle):
        self.__detalles.append(detalle)

    def calculate_total(self):
        return sum(d.get_subtotal() for d in self.__detalles)

    def get_id(self):
        return self.__id_venta

    def get_items(self):
        return list(self.__detalles)

    def get_event(self):
        return self.__evento

    def get_foodtruck(self):
        return self.__foodtruck

    def get_payment_method(self):
        return self.__metodo_pago

    def is_cancelled(self):
        return self.__anulado

    def cancel(self):
        if self.__anulado:
            raise ValueError(f"La venta #{self.__id_venta} ya está anulada.")
        self.__anulado = True

    def __str__(self):
        estado = " [ANULADA]" if self.__anulado else ""
        metodo = f" | {self.__metodo_pago.value}" if self.__metodo_pago else ""
        truck = f" | {self.__foodtruck.get_name()}" if self.__foodtruck else ""
        lineas = [
            f"\nVenta #{self.__id_venta}{estado} | {self.__fecha}{truck}{metodo} | Evento: {self.__evento.get_name()}",
            "  Productos:"
        ]
        for detalle in self.__detalles:
            lineas.append(f"    {detalle}")
        lineas.append(f"  Total: ${self.calculate_total():.2f}")
        return "\n".join(lineas)
