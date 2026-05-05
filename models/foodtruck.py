from models.inventory import Inventory
from models.receipt import Receipt


class Foodtruck:
    def __init__(self, id, name, license_plate=None, description=""):
        self.__id = id
        self.__name = name
        self.__license_plate = license_plate
        self.__description = description
        self.__active = True
        self.__inventory = Inventory()
        self.__staff = []
        self.__receipts = []
        self.__receipt_counter = 0

    def add_staff(self, user):
        for u in self.__staff:
            if u.get_id() == user.get_id():
                raise ValueError(f"El usuario '{user.get_login()}' ya está asignado a este foodtruck.")
        self.__staff.append(user)

    def open_receipt(self, cashier, payment_method, event_id=None):
        self.__receipt_counter += 1
        receipt = Receipt(self.__receipt_counter, self.__id, cashier.get_id(), payment_method, event_id)
        self.__receipts.append(receipt)
        return receipt

    def close_receipt(self, receipt):
        for item in receipt.get_items():
            self.__inventory.deduct_sale(item.get_menu_item(), item.get_quantity())
        receipt.close()

    def get_id(self):
        return self.__id

    def get_name(self):
        return self.__name

    def get_license_plate(self):
        return self.__license_plate

    def get_description(self):
        return self.__description

    def is_active(self):
        return self.__active

    def set_active(self, value):
        self.__active = value

    def get_inventory(self):
        return self.__inventory

    def get_staff(self):
        return list(self.__staff)

    def get_receipts(self):
        return list(self.__receipts)

    def __str__(self):
        plate = f" ({self.__license_plate})" if self.__license_plate else ""
        return f"{self.__name}{plate}"
