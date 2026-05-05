class ReceiptService:
    def __init__(self, foodtruck_repo, menu_item_repo, receipt_repo):
        self.__foodtruck_repo = foodtruck_repo
        self.__menu_item_repo = menu_item_repo
        self.__receipt_repo = receipt_repo

    def open(self, foodtruck_id, cashier, payment_method, event_id=None):
        ft = self.__foodtruck_repo.find_by_id(foodtruck_id)
        if not ft:
            raise ValueError(f"Foodtruck #{foodtruck_id} no encontrado.")
        return ft.open_receipt(cashier, payment_method, event_id)

    def add_item(self, receipt, menu_item_id, quantity):
        item = self.__menu_item_repo.find_by_id(menu_item_id)
        if not item:
            raise ValueError(f"Plato #{menu_item_id} no encontrado.")
        receipt.add_item(item, quantity)

    def close(self, foodtruck_id, receipt):
        ft = self.__foodtruck_repo.find_by_id(foodtruck_id)
        if not ft:
            raise ValueError(f"Foodtruck #{foodtruck_id} no encontrado.")
        ft.close_receipt(receipt)
        self.__receipt_repo.save(receipt)
        return receipt

    def cancel(self, receipt):
        receipt.cancel()

    def show_by_foodtruck(self, foodtruck_id):
        receipts = self.__receipt_repo.list_by_foodtruck(foodtruck_id)
        if not receipts:
            print("No hay tickets registrados.")
            return
        print(f"\n--- Tickets del foodtruck #{foodtruck_id} ---")
        for r in receipts:
            print(f"  {r}")

    def event_revenue(self, event_id):
        total = self.__receipt_repo.event_revenue(event_id)
        print(f"\nRecaudación del evento #{event_id}: ${total:.2f}")
        return total
