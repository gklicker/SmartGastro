from models.user import User
from models.role import Role


class UserRepository:
    def __init__(self):
        self.__users = []
        self.__next_id = 1

    def create(self, login, password, full_name, role):
        for u in self.__users:
            if u.get_login() == login:
                raise ValueError(f"Ya existe un usuario con login '{login}'")
        user = User(self.__next_id, login, password, full_name, role)
        self.__users.append(user)
        self.__next_id += 1
        return user

    def find_by_id(self, id):
        for u in self.__users:
            if u.get_id() == id:
                return u
        return None

    def find_by_login(self, login):
        for u in self.__users:
            if u.get_login() == login:
                return u
        return None

    def find_by_role(self, role):
        return [u for u in self.__users if u.get_role() == role]

    def list_all(self):
        return list(self.__users)

    def delete(self, id):
        for i, u in enumerate(self.__users):
            if u.get_id() == id:
                self.__users.pop(i)
                return True
        return False
