from enum import Enum


class EventStatus(Enum):
    PLANNED = "planned"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Event:
    def __init__(self, id, name, address, date_start, date_end, created_by, weather_forecast="Sin datos"):
        self.__id = id
        self.__name = name
        self.__address = address
        self.__date_start = date_start
        self.__date_end = date_end
        self.__created_by = created_by
        self.__status = EventStatus.PLANNED
        self.__weather_forecast = weather_forecast
        self.__cancellation_reason = None
        self.__cancellation_comment = None

    def get_id(self):
        return self.__id

    def get_name(self):
        return self.__name

    def get_address(self):
        return self.__address

    def get_date_start(self):
        return self.__date_start

    def get_date_end(self):
        return self.__date_end

    def get_status(self):
        return self.__status

    def get_weather_forecast(self):
        return self.__weather_forecast

    def start(self):
        if self.__status != EventStatus.PLANNED:
            raise ValueError("Solo se puede iniciar un evento planeado.")
        self.__status = EventStatus.ONGOING

    def complete(self):
        if self.__status != EventStatus.ONGOING:
            raise ValueError("Solo se puede completar un evento en curso.")
        self.__status = EventStatus.COMPLETED

    def cancel(self, reason, comment=""):
        if self.__status == EventStatus.COMPLETED:
            raise ValueError("No se puede cancelar un evento ya completado.")
        self.__status = EventStatus.CANCELLED
        self.__cancellation_reason = reason
        self.__cancellation_comment = comment

    def __str__(self):
        return (
            f"{self.__name} | {self.__address} | "
            f"{self.__date_start} → {self.__date_end} | "
            f"Estado: {self.__status.value} | Clima: {self.__weather_forecast}"
        )
