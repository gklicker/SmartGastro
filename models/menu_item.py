class MenuItem:
    def __init__(self, id, name, price, description=""):
        if price < 0:
            raise ValueError("El precio no puede ser negativo.")
        self.__id = id
        self.__name = name
        self.__price = price
        self.__description = description
        self.__ingredients = []
        self.__active = True

    def add_ingredient(self, ingredient, quantity):
        if quantity <= 0:
            raise ValueError("La cantidad del ingrediente debe ser mayor a cero.")
        self.__ingredients.append((ingredient, quantity))

    def get_id(self):
        return self.__id

    def get_name(self):
        return self.__name

    def get_price(self):
        return self.__price

    def get_description(self):
        return self.__description

    def get_ingredients(self):
        return list(self.__ingredients)

    def is_active(self):
        return self.__active

    def deactivate(self):
        self.__active = False

    def __str__(self):
        return f"{self.__name} | ${self.__price:.2f}"
