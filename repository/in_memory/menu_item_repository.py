from models.menu_item import MenuItem


class MenuItemRepository:
    def __init__(self):
        self.__items = []
        self.__next_id = 1

    def create(self, name, price, description=""):
        item = MenuItem(self.__next_id, name, price, description)
        self.__items.append(item)
        self.__next_id += 1
        return item

    def find_by_id(self, id):
        for item in self.__items:
            if item.get_id() == id:
                return item
        return None

    def list_active(self):
        return [item for item in self.__items if item.is_active()]

    def list_all(self):
        return list(self.__items)

    def delete(self, id):
        for idx, item in enumerate(self.__items):
            if item.get_id() == id:
                self.__items.pop(idx)
                return True
        return False
