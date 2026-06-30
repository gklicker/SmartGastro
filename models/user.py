import bcrypt
from models.role import Role


class User:
    def __init__(self, id, login, password, full_name, role):
        if not isinstance(role, Role):
            raise ValueError(f"Rol inválido: {role}")
        self.__id = id
        self.__login = login
        self.__password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(),
        )
        self.__full_name = full_name
        self.__role = role
        self.__active = True

    def get_id(self):
        return self.__id

    def get_login(self):
        return self.__login

    def get_full_name(self):
        return self.__full_name

    def get_role(self):
        return self.__role

    def is_active(self):
        return self.__active

    def deactivate(self):
        self.__active = False

    def check_password(self, password):
        return bcrypt.checkpw(password.encode("utf-8"), self.__password_hash)

    def __str__(self):
        estado = "activo" if self.__active else "inactivo"
        return f"{self.__full_name} | @{self.__login} | {self.__role.value} | {estado}"
