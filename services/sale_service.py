from models.event import Event
from models.receipt import Receipt, PaymentMethod
from external.weather import format_forecast
from datetime import datetime


class SaleService:
    def __init__(self, product_repo, receipt_repo, event_repo):
        self.__product_repo = product_repo
        self.__receipt_repo = receipt_repo
        self.__event_repo = event_repo

    def create_event(self, name, address, date, latitude, longitude):
        # We assume one day event for simplicity in CLI
        date_start = datetime.strptime(date, "%Y-%m-%d")
        date_end = date_start # Same day
        
        forecast = format_forecast(latitude, longitude)
        event_id = self.__event_repo.next_id()
        # created_by=1 as default for CLI
        event = Event(event_id, name, address, date_start, date_end, 1, forecast)
        self.__event_repo.add(event)
        print(f"✓ Evento creado: {event}")
        return event

    def register_sale(self, event_name, items):
        event = self.__event_repo.find_by_name(event_name)
        if not event:
            raise ValueError(f"Evento '{event_name}' no encontrado.")

        # For CLI, we use a simple Receipt
        # foodtruck_id=1, cashier_id=1, payment_method=CASH as defaults
        receipt_id = len(self.__receipt_repo.get_all()) + 1
        receipt = Receipt(receipt_id, 1, 1, PaymentMethod.CASH, event)

        for product_name, quantity in items:
            product = self.__product_repo.find_by_name(product_name)
            if not product:
                raise ValueError(f"Producto '{product_name}' no encontrado.")
            product.deduct_stock(quantity)
            receipt.add_item(product, quantity)

        receipt.close()
        self.__receipt_repo.add(receipt)
        return receipt

    def show_sales(self):
        sales = self.__receipt_repo.get_all()
        if not sales:
            print("No hay ventas registradas.")
            return
        print("\n--- Historial de ventas ---")
        for sale in sales:
            print(sale)
