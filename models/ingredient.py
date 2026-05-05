class Ingredient:
    def __init__(self, id, name, unit, min_stock_alert=0):
        self.__id = id
        self.__name = name
        self.__unit = unit
        self.__min_stock_alert = min_stock_alert

    def get_id(self):
        return self.__id

    def get_name(self):
        return self.__name

    def get_unit(self):
        return self.__unit

    def get_min_stock_alert(self):
        return self.__min_stock_alert

    def __str__(self):
        return f"{self.__name} ({self.__unit})"
