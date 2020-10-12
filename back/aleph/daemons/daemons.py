from back.aleph.memento import ConcreteMemento, Memento


class Daemon:
    def __init__(self, daemon_id, status="FREE"):
        self._state = None
        self.__daemon_id = daemon_id
        self.__status_daemon = status

    @property
    def daemon_id(self):
        return self.__daemon_id

    @property
    def status(self):
        return self.__status_daemon

    @status.setter
    def status(self, new_status):
        self.__status_daemon = new_status

    def save(self) -> ConcreteMemento:
        # todo: Cuando se modifica el estado?
        self._state = 'state de daemon'
        return ConcreteMemento(self._state)

    def restore(self, memento: Memento):
        self._state = memento.get_state()
        # todo: Igualar todos las propiedades necesarias
