class EventoRepository:
    def __init__(self):
        self.__eventos = []

    def add(self, evento):
        self.__eventos.append(evento)

    def get_all(self):
        return list(self.__eventos)

    def find_by_name(self, nombre):
        for evento in self.__eventos:
            if evento.get_name().lower() == nombre.lower():
                return evento
        return None

    def find_by_location(self, ubicacion):
        return [
            e for e in self.__eventos
            if ubicacion.lower() in e.get_location().lower()
        ]

    def find_by_date(self, fecha):
        return [e for e in self.__eventos if e.get_date() == fecha]
