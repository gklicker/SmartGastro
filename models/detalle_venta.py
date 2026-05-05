class DetalleVenta:
    def __init__(self, producto, cantidad):
        self.__producto = producto
        self.__cantidad = cantidad
        self.__precio_unitario = producto.get_price()

    def get_subtotal(self):
        return self.__precio_unitario * self.__cantidad

    def get_product(self):
        return self.__producto

    def get_quantity(self):
        return self.__cantidad

    def __str__(self):
        return (
            f"{self.__producto.get_name()} x{self.__cantidad} "
            f"@ ${self.__precio_unitario:.2f} = ${self.get_subtotal():.2f}"
        )
