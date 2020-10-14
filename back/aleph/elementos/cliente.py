import random
from back.aleph.config import Config
from back.aleph.mensajes import store
from back.aleph.salidas import add_all, add_result
from back.aleph.memento import ConcreteMemento, Memento


class Cliente:
    def __init__(self):
        self._state = None
        pass

    @staticmethod
    def store(nodo_info, event):
        destino = random.randint(Config.NODO_PROXY_LOWER, Config.NODO_PROXY_UPPER)  # ID del nodo
        # Los parametros vienen del cliente
        parametros = ["file", "file_name"]
        store(nodo_info, parametros, destino, event.extras)
        add_all(nodo_info, f'Mando Store al Proxy:{destino}', "cliente")

    def retrive(self):
        pass

    @staticmethod
    def confirm(nodo_info, event):
        add_result(nodo_info, event.parametros['id_copy'], "##Cliente##", "cliente")
        add_all(nodo_info, "LLego la confirmacion de mi storage", "cliente")

    def save(self) -> ConcreteMemento:
        # todo: Cuando se modifica el estado?
        self._state = "State de cliente"
        return ConcreteMemento(self._state)

    def restore(self, memento: Memento):
        self._state = memento.get_state()
        # todo: Igualar todos las propiedades necesarias
