import copy
import uuid

from back.aleph.daemons import Daemon
from back.aleph.mensajes import invokeTask, startTimer, insert, mensajeDaemon, confirmStorage, kill_clone
from back.aleph.salidas import add_result
from back.aleph.config import Config
from back.aleph.memento import ConcreteMemento, Memento


class T2Daemon(Daemon):
    def __init__(self, __daemon_id, __status="FREE"):
        super().__init__(__daemon_id, __status)
        self._state = None
        self.results = []
        self.clones_pendientes = []
        self.id_operacion = 0

    def execute(self, nodo_info, event):
        # add_result(nodo_info, event.parametros['id_copy'],
        #            f'Execute desde T2Daemon {event.target_element_id}', "t2daemon")
        self.status = "BUSY"
        # invokeOracle() le regresa el estado del nodo segun el HBManager, aqui supondremos que siempre lo manda
        parametros = copy.copy(event.parametros)
        if parametros['taskReplica'] == 0:
            # Solo entra aqui la primera vez
            parametros['taskReplica'] = 1
            parametros['id_operacion_t2daemon'] = self.id_operacion
            self.id_operacion += 1
            self.results.append(False)
            parametros['id_clone'] = uuid.uuid4()
            self.clones_pendientes.append(parametros['id_clone'])
            add_result(nodo_info, event.parametros['id_copy'], f"ID: {self.daemon_id} Creo clon y confirmo la "
                                                               f"operacion. {parametros['id_clone']}", "t2daemon")
            insert(nodo_info,
                   "T3DaemonID",
                   nodo_info.id,
                   nodo_info.id,
                   parametros,
                   event.prioridad,
                   event.operacion,
                   elemento_interno_remitente="t3daemon",
                   daemon_id=self.daemon_id,
                   nodo_objetivo=event.nodo_objetivo,
                   timer=Config.CLONE_TIMER,
                   charge_daemon="t2daemon",
                   )
            confirmStorage(nodo_info,
                           event.operacion,
                           nodo_info.id,
                           "buffer",
                           parametros,
                           event.nodo_objetivo,
                           remitente_interno="t2daemon",
                           remitente_interno_id=self.daemon_id)
        if parametros['id_clone'] in self.clones_pendientes:
            add_result(nodo_info, event.parametros['id_copy'], f"ID:{self.daemon_id} Mando operacion STORE "
                        f"de dispersos a nodo objetivo {event.nodo_objetivo} y programo timer", "t2daemon")
            invokeTask(nodo_info,
                       event.nodo_objetivo,
                       "STORE_DISPERSO",
                       parametros,
                       self.daemon_id,
                       "t2daemon")
            startTimer(nodo_info,
                       parametros,
                       event.operacion,
                       self.daemon_id,
                       event.nodo_objetivo,
                       event.prioridad,
                       "t2daemon")
        else:
            add_result(nodo_info, event.parametros['id_copy'], f"ID:{self.daemon_id} No se hace insert, ya se habia "
                                                               f"eliminado el clon", "t2daemon")
            # Ya se habia eliminado el clon segun t2daemon pero el t3daemon no sabia
            kill_clone(nodo_info, nodo_info.id,  parametros, "t2daemon", self.daemon_id)
            self.status = "FREE"
            mensajeDaemon(nodo_info, "FREE", self.daemon_id, "t2daemon", "2", event.parametros['id_copy'])

    def timer(self, nodo_info, event):
        # add_result(nodo_info, event.parametros['id_copy'], "Timer T2 Daemon, se hace insert", "t2daemon")
        # LLego resultado
        # TODO: Esto esta al reves
        if self.results[event.parametros['id_operacion_t2daemon']]:
            add_result(nodo_info, event.parametros['id_copy'],
                       f"{self.daemon_id} Timer: LLego la respuesta antes de expirar el timer, el clon ya se elimino. No hago insert",
                       "t2daemon")
        else:
            add_result(nodo_info, event.parametros['id_copy'],
                       f"ID:{self.daemon_id} Timer: No ha llegado la respuesta de la operacion {event.operacion},hago insert", "t2daemon")
            event.parametros['taskReplica'] += 1
            insert(nodo_info,
                   "T2DaemonID",
                   nodo_info.id,
                   nodo_info.id,
                   event.parametros,
                   event.prioridad,
                   event.operacion,
                   elemento_interno_remitente="t2daemon",
                   nodo_objetivo=event.nodo_objetivo,
                   daemon_id=self.daemon_id
                   )
        self.status = "FREE"
        mensajeDaemon(nodo_info, "FREE", self.daemon_id, "t2daemon", "2", event.parametros['id_copy'])

    def confirm(self, nodo_info, event):
        if self.results[event.parametros['id_operacion_t2daemon']]:
            add_result(nodo_info, event.parametros['id_copy'],
                       f"ID:{self.daemon_id} Ya se habia confirmado esta la operacion {event.operacion}")
        else:
            add_result(nodo_info, event.parametros['id_copy'],
                       f"ID:{self.daemon_id} LLega confirmacion de operacion. Tengo que matar al clon: {event.parametros['id_clone']}",
                       "t2daemon")
            self.results[event.parametros['id_operacion_t2daemon']] = True
            parametros = {'id_clone': event.parametros['id_clone'], 'id_copy': event.parametros['id_copy']}
            kill_clone(nodo_info, nodo_info.id,  parametros, "t2daemon", self.daemon_id)
            try:
                self.clones_pendientes.remove(event.parametros['id_clone'])
            except ValueError:
                print(f"Nodo:{nodo_info.id}. T2Daemon: {self.daemon_id}.Alguien mas habia elimnado este clon")

    def save(self) -> ConcreteMemento:
        # todo: Cuando se modifica el estado?
        self._state = 'state de daemon'
        return ConcreteMemento(self._state)

    def restore(self, memento: Memento):
        self._state = memento.get_state()
        # todo: Igualar todos las propiedades necesarias
