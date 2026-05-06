class Product:
    def __init__(self, id, name, price, stock, min_stock=5):
        self.__id = id
        self.__name = name
        self.__price = price
        self.__stock = stock
        self.__min_stock = min_stock

    def get_id(self):
        return self.__id

    def get_name(self):
        return self.__name

    def get_price(self):
        return self.__price

    def get_stock(self):
        return self.__stock

    def get_min_stock(self):
        return self.__min_stock

    def set_stock(self, quantity):
        if quantity < 0:
            raise ValueError("El stock no puede ser negativo.")
        self.__stock = quantity

    def deduct_stock(self, quantity):
        if quantity <= 0:
            raise ValueError("La cantidad a descontar debe ser mayor a cero.")
        if self.__stock == 0:
            raise ValueError(f"Sin stock disponible para '{self.__name}'.")
        if quantity > self.__stock:
            raise ValueError(
                f"Stock insuficiente para '{self.__name}'. "
                f"Disponible: {self.__stock}, solicitado: {quantity}."
            )
        self.__stock -= quantity

    def has_low_stock(self):
        return self.__stock <= self.__min_stock

    def __str__(self):
        alert = " ⚠ STOCK BAJO" if self.has_low_stock() else ""
        return (
            f"{self.__name} | "
            f"Precio: ${self.__price:.2f} | "
            f"Stock: {self.__stock}{alert}"
        )
