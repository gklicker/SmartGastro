from models.event import Event, EventStatus
from datetime import datetime


class EventRepository:
    def __init__(self):
        self.__events = []
        self.__next_id = 1

    def create(self, name, address, date_start, date_end, created_by):
        event = Event(self.__next_id, name, address, date_start, date_end, created_by)
        self.__events.append(event)
        self.__next_id += 1
        return event

    def find_by_id(self, id):
        for e in self.__events:
            if e.get_id() == id:
                return e
        return None

    def list_by_status(self, status):
        return [e for e in self.__events if e.get_status() == status]

    def list_upcoming(self):
        now = datetime.now()
        active = [EventStatus.PLANNED, EventStatus.ONGOING]
        return [e for e in self.__events if e.get_status() in active and e.get_date_end() >= now]

    def list_all(self):
        return list(self.__events)

    def delete(self, id):
        for idx, e in enumerate(self.__events):
            if e.get_id() == id:
                self.__events.pop(idx)
                return True
        return False
