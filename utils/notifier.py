# Implements the observer pattern. In this case "Listener" is the observer and "Notifier" is the subject.
from typing import List

from utils.listener import Listener


class Notifier:
    def __init__(self):
        self.__listeners = list()  # type: List[Listener]
        self.__values = dict()  # type: dict[str, any]

    def add_listener(self, listener: Listener):
        if listener not in self.__listeners:
            self.__listeners.append(listener)

    def remove_listener(self, listener: Listener):
        try:
            self.__listeners.remove(listener)
        except ValueError:
            print("Listener not found: " + str(listener))

    def notify_listeners(self, property_name: str, value: any):
        if self.__values.get(property_name) == value:
            return

        for listener in self.__listeners:
            listener.update(property_name, value)
