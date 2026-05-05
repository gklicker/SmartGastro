class Producto:
    def __init__(self, nombre, precio, stock, stock_minimo=5):
        self.__nombre = nombre
        self.__precio = precio
        self.__stock = stock
        self.__stock_minimo = stock_minimo

    def get_name(self):
        return self.__nombre

    def get_price(self):
        return self.__precio

    def get_stock(self):
        return self.__stock

    def get_min_stock(self):
        return self.__stock_minimo

    def set_stock(self, cantidad):
        if cantidad < 0:
            raise ValueError("El stock no puede ser negativo.")
        self.__stock = cantidad

    def deduct_stock(self, cantidad):
        if cantidad <= 0:
            raise ValueError("La cantidad a descontar debe ser mayor a cero.")
        if self.__stock == 0:
            raise ValueError(f"Sin stock disponible para '{self.__nombre}'.")
        if cantidad > self.__stock:
            raise ValueError(
                f"Stock insuficiente para '{self.__nombre}'. "
                f"Disponible: {self.__stock}, solicitado: {cantidad}."
            )
        self.__stock -= cantidad

    def has_low_stock(self):
        return self.__stock <= self.__stock_minimo

    def __str__(self):
        alerta = " ⚠ STOCK BAJO" if self.has_low_stock() else ""
        return (
            f"{self.__nombre} | "
            f"Precio: ${self.__precio:.2f} | "
            f"Stock: {self.__stock}{alerta}"
        )
