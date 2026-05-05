class FoodtruckService:
    def __init__(self, foodtruck_repo, ingredient_repo):
        self.__foodtruck_repo = foodtruck_repo
        self.__ingredient_repo = ingredient_repo

    def create(self, name, license_plate=None, description=""):
        return self.__foodtruck_repo.create(name, license_plate, description)

    def add_stock(self, foodtruck_id, ingredient_name, quantity):
        ft = self.__foodtruck_repo.find_by_id(foodtruck_id)
        if not ft:
            raise ValueError(f"Foodtruck #{foodtruck_id} no encontrado.")
        ingredient = self.__ingredient_repo.find_by_name(ingredient_name)
        if not ingredient:
            raise ValueError(f"Ingrediente '{ingredient_name}' no encontrado.")
        ft.get_inventory().add_stock(ingredient, quantity)
        return ft

    def show_inventory(self, foodtruck_id):
        ft = self.__foodtruck_repo.find_by_id(foodtruck_id)
        if not ft:
            raise ValueError(f"Foodtruck #{foodtruck_id} no encontrado.")
        stock = ft.get_inventory().get_stock()
        if not stock:
            print("El inventario está vacío.")
            return
        print(f"\n--- Inventario: {ft.get_name()} ---")
        for ing_id, qty in stock.items():
            ingredient = self.__ingredient_repo.find_by_id(ing_id)
            if ingredient:
                alerta = " ⚠ STOCK BAJO" if ft.get_inventory().is_below_min(ingredient) else ""
                print(f"  {ingredient.get_name()}: {qty} {ingredient.get_unit()}{alerta}")

    def get_alerts(self, foodtruck_id):
        ft = self.__foodtruck_repo.find_by_id(foodtruck_id)
        if not ft:
            raise ValueError(f"Foodtruck #{foodtruck_id} no encontrado.")
        alerts = []
        for ing_id, qty in ft.get_inventory().get_stock().items():
            ingredient = self.__ingredient_repo.find_by_id(ing_id)
            if ingredient and ft.get_inventory().is_below_min(ingredient):
                alerts.append((ingredient, qty))
        return alerts

    def list_all(self):
        return self.__foodtruck_repo.list_all()

    def add_staff(self, foodtruck_id, user):
        ft = self.__foodtruck_repo.find_by_id(foodtruck_id)
        if not ft:
            raise ValueError(f"Foodtruck #{foodtruck_id} no encontrado.")
        ft.add_staff(user)
