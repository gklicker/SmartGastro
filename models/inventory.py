class Inventory:
    def __init__(self):
        self.__stock = {}

    def add_stock(self, ingredient, quantity):
        if quantity <= 0:
            raise ValueError("La cantidad debe ser mayor a cero.")
        id = ingredient.get_id()
        self.__stock[id] = self.__stock.get(id, 0) + quantity

    def deduct_stock(self, ingredient, quantity):
        if quantity <= 0:
            raise ValueError("La cantidad debe ser mayor a cero.")
        id = ingredient.get_id()
        available = self.__stock.get(id, 0)
        if available < quantity:
            raise ValueError(
                f"Stock insuficiente de '{ingredient.get_name()}'. "
                f"Disponible: {available} {ingredient.get_unit()}, necesario: {quantity}."
            )
        self.__stock[id] -= quantity

    def get_quantity(self, ingredient):
        return self.__stock.get(ingredient.get_id(), 0)

    def is_below_min(self, ingredient):
        return self.get_quantity(ingredient) < ingredient.get_min_stock_alert()

    def can_sell(self, menu_item, quantity=1):
        for ingredient, qty_needed in menu_item.get_ingredients():
            available = self.__stock.get(ingredient.get_id(), 0)
            if available < qty_needed * quantity:
                return False
        return True

    def available_portions(self, menu_item):
        ingredients = menu_item.get_ingredients()
        if not ingredients:
            return 0
        min_portions = None
        for ingredient, qty_needed in ingredients:
            available = self.__stock.get(ingredient.get_id(), 0)
            portions = int(available // qty_needed)
            if min_portions is None or portions < min_portions:
                min_portions = portions
        return min_portions

    def deduct_sale(self, menu_item, quantity=1):
        if not self.can_sell(menu_item, quantity):
            raise ValueError(f"Stock insuficiente para vender {quantity} x '{menu_item.get_name()}'.")
        for ingredient, qty_needed in menu_item.get_ingredients():
            self.__stock[ingredient.get_id()] -= qty_needed * quantity

    def get_stock(self):
        return dict(self.__stock)

    def __str__(self):
        return f"Inventario con {len(self.__stock)} ingredientes"
