from models.ingredient import Ingredient


class IngredientRepository:
    def __init__(self):
        self.__ingredients = []
        self.__next_id = 1

    def create(self, name, unit, min_stock_alert=0):
        ingredient = Ingredient(self.__next_id, name, unit, min_stock_alert)
        self.__ingredients.append(ingredient)
        self.__next_id += 1
        return ingredient

    def find_by_id(self, id):
        for i in self.__ingredients:
            if i.get_id() == id:
                return i
        return None

    def find_by_name(self, name):
        for i in self.__ingredients:
            if i.get_name().lower() == name.lower():
                return i
        return None

    def list_all(self):
        return list(self.__ingredients)

    def delete(self, id):
        for idx, i in enumerate(self.__ingredients):
            if i.get_id() == id:
                self.__ingredients.pop(idx)
                return True
        return False
