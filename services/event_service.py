from external.weather import format_forecast


class EventService:
    def __init__(self, event_repo):
        self.__event_repo = event_repo

    def create(self, name, address, date_start, date_end, created_by):
        return self.__event_repo.create(name, address, date_start, date_end, created_by)

    def start(self, event_id):
        event = self.__get_or_raise(event_id)
        event.start()
        return event

    def complete(self, event_id):
        event = self.__get_or_raise(event_id)
        event.complete()
        return event

    def cancel(self, event_id, reason, comment=""):
        event = self.__get_or_raise(event_id)
        event.cancel(reason, comment)
        return event

    def get_forecast(self, latitude, longitude):
        return format_forecast(latitude, longitude)

    def list_upcoming(self):
        return self.__event_repo.list_upcoming()

    def show_upcoming(self):
        events = self.list_upcoming()
        if not events:
            print("No hay eventos próximos.")
            return
        print("\n--- Eventos próximos ---")
        for e in events:
            print(f"  #{e.get_id()} {e}")

    def __get_or_raise(self, event_id):
        event = self.__event_repo.find_by_id(event_id)
        if not event:
            raise ValueError(f"Evento #{event_id} no encontrado.")
        return event
