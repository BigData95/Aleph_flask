import random
from .config import Config
from .mensajes import store
from .salidas import add_all
from .memento import ConcreteMemento, Memento


class Cliente:
    def __init__(self):
        self._state = None
        pass

    @staticmethod
    def store(nodo_info):
        destino = random.randint(Config.NODO_PROXY_LOWER, Config.NODO_PROXY_UPPER)  # ID del nodo
        # Los parametros vienen del cliente
        parametros = ["file", "file_name"]
        store(nodo_info, parametros, destino)
        add_all(nodo_info, f'Mando Store al Proxy:{destino}')

    def retrive(self):
        pass

    @staticmethod
    def confirm(nodo_info, event):
        add_all(nodo_info, f"LLego la confirmacion de mi storage", "cliente")

    def save(self) -> ConcreteMemento:
        # todo: Cuando se modifica el estado?
        self._state = "State de cliente"
        return ConcreteMemento(self._state)

    def restore(self, memento: Memento):
        self._state = memento.get_state()
        # todo: Igualar todos las propiedades necesarias
