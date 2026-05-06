from datetime import datetime
from enum import Enum


class ReceiptStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentMethod(Enum):
    CASH = "cash"
    CARD = "card"
    MERCADOPAGO = "mercadopago"


class ReceiptItem:
    def __init__(self, menu_item, quantity, unit_price):
        self.__menu_item = menu_item
        self.__quantity = quantity
        self.__unit_price = unit_price

    def get_menu_item(self):
        return self.__menu_item

    def get_quantity(self):
        return self.__quantity

    def get_unit_price(self):
        return self.__unit_price

    def get_subtotal(self):
        return self.__quantity * self.__unit_price

    def __str__(self):
        return f"{self.__menu_item.get_name()} x{self.__quantity} = ${self.get_subtotal():.2f}"


class Receipt:
    def __init__(self, id, foodtruck_id, cashier_id, payment_method, event=None):
        self.__id = id
        self.__foodtruck_id = foodtruck_id
        self.__cashier_id = cashier_id
        self.__payment_method = payment_method
        self.__event = event # Can be object or ID
        self.__status = ReceiptStatus.OPEN
        self.__items = []
        self.__created_at = datetime.now()
        self.__closed_at = None

    def add_item(self, menu_item, quantity):
        if self.__status != ReceiptStatus.OPEN:
            raise ValueError("No se puede agregar items a un ticket cerrado.")
        if quantity <= 0:
            raise ValueError("La cantidad debe ser mayor a cero.")
        # MenuItem or Product object should have is_active or we assume True for now
        active = getattr(menu_item, 'is_active', lambda: True)()
        if not active:
            raise ValueError(f"El plato '{menu_item.get_name()}' no está disponible.")
        self.__items.append(ReceiptItem(menu_item, quantity, menu_item.get_price()))

    def close(self):
        if self.__status != ReceiptStatus.OPEN:
            raise ValueError(f"El ticket no está abierto. Estado actual: {self.__status.value}.")
        if not self.__items:
            raise ValueError("No se puede cerrar un ticket vacío.")
        self.__status = ReceiptStatus.CLOSED
        self.__closed_at = datetime.now()

    def cancel(self):
        if self.__status == ReceiptStatus.CLOSED:
             raise ValueError("No se puede cancelar un ticket ya cerrado.")
        self.__status = ReceiptStatus.CANCELLED

    def get_id(self):
        return self.__id

    def get_foodtruck_id(self):
        return self.__foodtruck_id

    def get_cashier_id(self):
        return self.__cashier_id

    def get_event(self):
        return self.__event

    def get_status(self):
        return self.__status

    def get_items(self):
        return list(self.__items)

    def get_total(self):
        return sum(item.get_subtotal() for item in self.__items)

    def get_payment_method(self):
        return self.__payment_method

    def get_created_at(self):
        return self.__created_at

    def get_closed_at(self):
        return self.__closed_at

    def __str__(self):
        status_text = " [ANULADO]" if self.__status == ReceiptStatus.CANCELLED else ""
        date_str = self.__created_at.strftime("%Y-%m-%d %H:%M")
        event_name = self.__event.get_name() if hasattr(self.__event, 'get_name') else str(self.__event)
        
        lines = [
            f"\nTicket #{self.__id}{status_text} | {date_str} | Evento: {event_name}",
            "  Productos:"
        ]
        for item in self.__items:
            lines.append(f"    {item}")
        lines.append(f"  Total: ${self.get_total():.2f}")
        return "\n".join(lines)
