
import copy

from back.aleph.daemons import Daemon
from back.aleph.mensajes import insert, startTimerClone
from back.aleph.salidas import add_result
from back.aleph.memento import ConcreteMemento, Memento


class T3Daemon(Daemon):
    def __init__(self, __daemon_id, __status='FREE'):
        super().__init__(__daemon_id)
        self._state = None
        self.__clones = []
        # self.__matar_clon = list()
        # self.__parametros = None

    def execute(self, nodo_info, event):
        parametros = copy.copy(event.parametros)
        add_result(nodo_info, parametros['id_copy'], f"LLega clon {event.parametros['id_clone']}. Inicio timer", "t3daemon")
        # Create clone, ya debe de venir dentro de los parametros
        self.__clones.append(event.parametros['id_clone'])
        parametros['prioridad'] = event.prioridad
        parametros['nodo_objetivo'] = event.nodo_objetivo
        parametros['source_id'] = event.source_element_id
        startTimerClone(nodo_info,
                        event.parametros['timer'],
                        event.operacion,
                        parametros,
                        self.daemon_id
                        )

    def timer(self, nodo_info, event):
        add_result(nodo_info, event.parametros['id_copy'], "Expira timer", "t3daemon")
        if event.parametros['id_clone'] in self.__clones:
            add_result(nodo_info, event.parametros['id_copy'], f'Mando insert a {event.parametros["charge_daemon"]}'
                        f' Id:{event.parametros["source_id"]} de nodo {event.parametros["nodo_objetivo"]}', "t3daemon")
            if event.parametros['charge_daemon'] == "t1daemon":
                daemon = "T1DaemonID"
            else:  # if event.parametros['charge_daemon'] == "T2DaemonID":
                daemon = "T2DaemonID"
            insert(nodo_info,
                   daemon,  # event.parametros['charge_daemon'],
                   nodo_info.id,
                   nodo_info.id,
                   event.parametros,
                   event.parametros['prioridad'],
                   event.operacion,
                   elemento_interno_remitente="t3Daemon",
                   nodo_objetivo=event.parametros['nodo_objetivo'],
                   daemon_id=event.parametros['source_id']
                   )
        else:
            add_result(nodo_info, event.parametros['id_copy'], f"Este clon {event.parametros['id_clone']} "
                                                               f"ya se mato, no se hace insert", "t3daemon")

    def kill(self, nodo_info, event):
        if event.source_element == "proxy":
            add_result(nodo_info,event.parametros['id_copy'], f"El proxy {event.source} nos pide matar al clon {event.parametros['id_clone']}", "t3daemon")
        if event.parametros['id_clone'] in self.__clones:
            add_result(nodo_info, event.parametros['id_copy'],
                       f"Kill: LLega mensaje para eliminar clon {event.parametros['id_clone']}, lo eliminamos", "t3daemon")
            self.__clones.remove(event.parametros['id_clone'])
        else:
            add_result(nodo_info, event.parametros['id_copy'], f"El clon {event.parametros['id_clone']} "
                        f"ya se habia eliminado, despachado o no ha llegado su timer", "t3daemon")

    def save(self) -> ConcreteMemento:
        # todo: Cuando se modifica el estado?
        self._state = 'state de daemon'
        return ConcreteMemento(self._state)

    def restore(self, memento: Memento):
        self._state = memento.get_state()
        # todo: Igualar todos las propiedades necesarias
