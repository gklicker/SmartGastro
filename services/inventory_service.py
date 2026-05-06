from models.product import Product


class InventoryService:
    def __init__(self, product_repo):
        self.__product_repo = product_repo

    def get_product(self, name):
        return self.__product_repo.find_by_name(name)

    def add_product(self, name, price, stock, min_stock=5):
        product_id = self.__product_repo.next_id()
        product = Product(product_id, name, price, stock, min_stock)
        self.__product_repo.add(product)
        return product

    def add_stock(self, name, quantity):
        product = self.__product_repo.find_by_name(name)
        if not product:
            raise ValueError(f"Producto '{name}' no encontrado.")
        product.set_stock(product.get_stock() + quantity)
        return product

    def show_inventory(self):
        products = self.__product_repo.get_all()
        if not products:
            print("El inventario está vacío.")
            return
        print("\n--- Inventario ---")
        for product in products:
            print(f"  {product}")

    def check_alerts(self):
        alerts = [p for p in self.__product_repo.get_all() if p.has_low_stock()]
        if alerts:
            print("\nAlerta de stock bajo:")
            for p in alerts:
                print(f"  - {p.get_name()}: {p.get_stock()} unidades")
