from models.receipt import ReceiptStatus


class ReceiptRepository:
    def __init__(self):
        self.__receipts = []

    def save(self, receipt):
        if receipt not in self.__receipts:
            self.__receipts.append(receipt)
        return receipt

    def add(self, receipt):
        return self.save(receipt)

    def find_by_id(self, id):
        for r in self.__receipts:
            if r.get_id() == id:
                return r
        return None

    def list_by_foodtruck(self, foodtruck_id):
        return [r for r in self.__receipts if r.get_foodtruck_id() == foodtruck_id]

    def list_by_event(self, event_id):
        return [r for r in self.__receipts if r.get_event_id() == event_id]

    def event_revenue(self, event_id):
        return sum(
            r.get_total()
            for r in self.__receipts
            if r.get_event() == event_id and r.get_status() == ReceiptStatus.CLOSED
        )

    def get_all(self):
        return list(self.__receipts)

    def list_all(self):
        return self.get_all()
