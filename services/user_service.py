class UserService:
    def __init__(self, user_repo):
        self.__user_repo = user_repo

    def create(self, login, password, full_name, role):
        return self.__user_repo.create(login, password, full_name, role)

    def authenticate(self, login, password):
        user = self.__user_repo.find_by_login(login)
        if not user:
            raise ValueError(f"Usuario '{login}' no encontrado.")
        if not user.is_active():
            raise ValueError(f"El usuario '{login}' está inactivo.")
        if not user.check_password(password):
            raise ValueError("Contraseña incorrecta.")
        return user

    def deactivate(self, login):
        user = self.__user_repo.find_by_login(login)
        if not user:
            raise ValueError(f"Usuario '{login}' no encontrado.")
        user.deactivate()

    def list_all(self):
        return self.__user_repo.list_all()

    def find_by_login(self, login):
        return self.__user_repo.find_by_login(login)
