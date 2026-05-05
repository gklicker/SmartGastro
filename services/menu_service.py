class MenuService:
    def __init__(self, ingredient_repo, menu_item_repo):
        self.__ingredient_repo = ingredient_repo
        self.__menu_item_repo = menu_item_repo

    def create_ingredient(self, name, unit, min_stock_alert=0):
        if self.__ingredient_repo.find_by_name(name):
            raise ValueError(f"El ingrediente '{name}' ya existe.")
        return self.__ingredient_repo.create(name, unit, min_stock_alert)

    def create_item(self, name, price, description=""):
        return self.__menu_item_repo.create(name, price, description)

    def add_ingredient_to_item(self, menu_item_id, ingredient_name, quantity):
        item = self.__menu_item_repo.find_by_id(menu_item_id)
        if not item:
            raise ValueError(f"Plato #{menu_item_id} no encontrado.")
        ingredient = self.__ingredient_repo.find_by_name(ingredient_name)
        if not ingredient:
            raise ValueError(f"Ingrediente '{ingredient_name}' no encontrado.")
        item.add_ingredient(ingredient, quantity)
        return item

    def deactivate_item(self, menu_item_id):
        item = self.__menu_item_repo.find_by_id(menu_item_id)
        if not item:
            raise ValueError(f"Plato #{menu_item_id} no encontrado.")
        item.deactivate()

    def show_menu(self):
        items = self.__menu_item_repo.list_active()
        if not items:
            print("No hay platos disponibles.")
            return
        print("\n--- Menú ---")
        for item in items:
            print(f"  #{item.get_id()} {item}")
            for ingredient, qty in item.get_ingredients():
                print(f"      - {ingredient.get_name()}: {qty} {ingredient.get_unit()}")

    def show_ingredients(self):
        ingredients = self.__ingredient_repo.list_all()
        if not ingredients:
            print("No hay ingredientes registrados.")
            return
        print("\n--- Ingredientes ---")
        for ing in ingredients:
            print(f"  #{ing.get_id()} {ing}")
