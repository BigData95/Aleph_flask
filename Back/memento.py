from abc import ABC, abstractmethod
from datetime import datetime


class Memento(ABC):

    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def get_date(self):
        pass

    # @abstractmethod
    # def get_state(self):
    #     pass


class ConcreteMemento(Memento):
    def __init__(self, state):
        self._state = state
        self._date = str(datetime.now())[:19]

    def get_state(self):
        return self._state

    def get_name(self):
        return f'{self._date}'  # / {self._state[0:9]}'

    def get_date(self):
        return self._date


class Caretaker:
    def __init__(self, originator):
        self._mementos = []
        self._originator = originator

    def save(self):
        print("Saving Originator's state...")
        self._mementos.append(self._originator.save())

    def restore(self):
        length_mementos = len(self._mementos)
        if not length_mementos:
            return
        memento = self._mementos.pop()
        print(f'Carataker: Restoring state to: {memento.get_name()}')
        try:
            self._originator.restore(memento)
        except Exception:
            self.restore()
