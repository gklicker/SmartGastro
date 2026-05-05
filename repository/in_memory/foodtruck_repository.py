from models.foodtruck import Foodtruck


class FoodtruckRepository:
    def __init__(self):
        self.__foodtrucks = []
        self.__next_id = 1

    def create(self, name, license_plate=None, description=""):
        ft = Foodtruck(self.__next_id, name, license_plate, description)
        self.__foodtrucks.append(ft)
        self.__next_id += 1
        return ft

    def find_by_id(self, id):
        for ft in self.__foodtrucks:
            if ft.get_id() == id:
                return ft
        return None

    def list_active(self):
        return [ft for ft in self.__foodtrucks if ft.is_active()]

    def list_all(self):
        return list(self.__foodtrucks)

    def delete(self, id):
        for idx, ft in enumerate(self.__foodtrucks):
            if ft.get_id() == id:
                self.__foodtrucks.pop(idx)
                return True
        return False
