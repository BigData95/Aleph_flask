# from StorageProcessMsg import T1_TIMER_STATE
from .mensajes import *
from .salidas import add_result, add_all, Config
from .memento import ConcreteMemento, Caretaker, Memento

import copy

"""

"""

T1_TIMER_STATE = 3


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


# Cuidado antes los status eran status_daemon
class T1Daemon(Daemon):
    def __init__(self, daemon_id, status="FREE"):
        Daemon.__init__(self, daemon_id, status)
        self._state = None
        self.__status = None
        self.results = []  
        self.__id_operacion = 0


    # @staticmethod
    def execute(self, nodo_info, event):
        # TODO: Documentar que tiene los parametros
        add_result(nodo_info, event.parametros['id_copy'],
                   f'Execute desde T1Daemon {event.target_element_id}', "t1daemon")
        if nodo_info.target_status == "suspected":
            add_result(nodo_info, event.parametros['id_file'],
                       f"T1Daemon:{self.daemon_id} Target is suspected.", "t1daemon")
            report(self,
                   "FAILURE",
                   self.daemon_id,
                   event.parametros,
                   event.prioridad,
                   event.operacion,
                   event.nodo_objetivo)
        else:  # Target is supposed to be ok
            self.__status = "BUSY"
            parametros = copy.copy(event.parametros)
            if 'timer_state' not in parametros:
                parametros['timer_state'] = 0
                parametros['id_operacion'] = self.__id_operacion 
                self.__id_operacion += 1
                self.results.append('FALSE')
            # self.__timer_state = parametros['timer_state']
            add_result(nodo_info, event.parametros['id_copy'], "t1Class: Mando Invoketask", "t1daemon")
            invokeTask(nodo_info,
                       event.nodo_objetivo,
                       event.operacion,
                       parametros,
                       self.daemon_id
                       )
            startTimer(nodo_info,
                       parametros,  # Incluye ahora timer_state
                       event.operacion,
                       self.daemon_id,
                       event.nodo_objetivo,
                       event.prioridad
                       )  # TODO: Agregar la variable del timer
            add_result(nodo_info, event.parametros['id_copy'], "t1Class: Mando Timer", "t1daemon")

    # Cambiar por expiringTimer()
    def timer(self, nodo_info, event):
        """Utiliza nodo_info para obtener la informacion del nodo donde vive, como el id y el clock """
        add_result(nodo_info, event.parametros['id_copy'],
                   f'Timer desde T1Daemon {event.target_element_id}', "t1daemon")
        parametros = copy.copy(event.parametros)
        index_operacion = event.parametros["id_operacion"]
        if self.results[index_operacion]:
            """Ya llego la confirmacion de que la tarea se completo, el daemon queda libre y se tiene que limpiar
            los atributos para futuros usos distintos a storage
            """
            add_result(nodo_info, event.parametros['id_copy'], "LLego el resultado antes de expirar el timer",
                       "t1daemon")
            pass
        else:
            if parametros['timer_state'] < Config.T1_TIMER_STATE:
                parametros["timer_state"] += 1
                add_result(nodo_info, parametros['id_copy'], "Hago insert pues no recibi respuesta", "t1daemon")
                insert(nodo_info,
                       "T1DaemonID",
                       nodo_info.id,
                       nodo_info.id,
                       parametros,
                       event.prioridad,
                       event.operacion,
                       elemento_interno_remitente="t1daemon",
                       nodo_objetivo=event.nodo_objetivo,
                       daemon_id = self.daemon_id
                       )
            else:
                add_result(nodo_info, parametros['id_copy'], "Debemos reportar la falla", "t1daemon")
                parametros["reported"] += 1
                report(nodo_info,
                       "FAILURE",
                       self.daemon_id,
                       parametros,
                       event.nodo_objetivo,
                       event.prioridad,
                       event.operacion
                       )
            # Aviso que ya estoy disponible
        self.__status = "FREE"
        mensajeDaemon(nodo_info, "FREE", self.daemon_id, "1")
        # TODO: Como esta libre debria limpiar su parametros
        # TODO: CleanParametros()

    def confirm(self, nodo_info, event):
        # TODO: Se deberia de usar event porque todo lo de self esta vacio
        """
        Cuando llega una confirmacion del nodo a quien se le mando el trabajo, manda el report con SUCESS \n
        No le importa el estado del timer. Pero con self.results le avisa al timer 
        """
        print(f"{self.daemon_id}:Parametros confirm {event.parametros}")
        add_result(nodo_info, event.parametros['id_copy'],
                   f"T1Daemon:{self.daemon_id}: Llego confirmacion de la operacion desde nodo:{event.source}, Mando report",
                   "t1daemon")
        index_operacion = event.parametros["id_operacion"]
        self.results[index_operacion] = True
        report(nodo_info, "SUCESS", self.daemon_id, event.parametros, event.nodo_objetivo, operacion=event.operacion)

    def save(self) -> ConcreteMemento:
        # todo: Cuando se modifica el estado?
        self._state = 'state de daemon'
        print(f"SOY T1 DAMEON ESTE ES MI STATE: {self._state}: {self.daemon_id}")
        return ConcreteMemento(self._state)

    def restore(self, memento: Memento):
        self._state = memento.get_state()
        # todo: Igualar todos las propiedades necesarias

    def clean(self):
        self.__nodo_objetivo = None
        self.__prioridad = None
        self.__operacion = None
        self.__timer_state = 0


class T2Daemon(Daemon):
    def __init__(self, __daemon_id, __status="FREE"):
        super().__init__(__daemon_id, __status)
        self._state = None

    def execute(self, nodo_info, event):
        add_result(nodo_info, event.parametros['id_copy'],
                   f'Execute desde T2Daemon {event.target_element_id}', "t2Daemon")
        print("Execute de t2Daemon")

    def save(self) -> ConcreteMemento:
        # todo: Cuando se modifica el estado?
        self._state = 'state de daemon'
        return ConcreteMemento(self._state)

    def restore(self, memento: Memento):
        self._state = memento.get_state()
        # todo: Igualar todos las propiedades necesarias


class T3Daemon(Daemon):
    def __init__(self, __daemon_id, __status='FREE'):
        super().__init__(__daemon_id)
        self._state = None
        self.__clones = list()
        self.__clone_id = 0
        self.__matar_clon = list()
        # self.__parametros = None

    def execute(self, nodo_info, event):
        parametros = copy.copy(event.parametros)
        add_result(nodo_info, parametros['id_copy'], "Execute Daemon 3, inicio timer", "t3daemon")
        # Create clone
        self.__clones.append(self.__clone_id)
        self.__clone_id += 1

        parametros['prioridad'] = event.prioridad
        parametros['clone_id'] = self.__clone_id
        parametros['nodo_objetivo'] = event.nodo_objetivo
        startTimerClone(nodo_info,
                        event.parametros['timer'],
                        event.operacion,
                        parametros,
                        self.daemon_id
                        )

    def timer(self, nodo_info, nodo_id, event):
        add_result(nodo_info, event.parametros['id_copy'], "Timer de T3Daemon", "t3daemon")
        if nodo_id not in self.__matar_clon:
            # Para t1Daemon
            parametros_envio = {
                'file': event.parametros['file'],
                'id_file': event.parametros['id_file'],
                'id_copy': event.parametros['id_copy'],
                'new_id_copy': event.parametros['new_id_copy'],
                'reported': 0
            }
            add_result(nodo_info, event.parametros['id_copy'], "Mando insert", "t3daemon")
            if event.parametros['charge_daemon'] == "t1daemon":
                daemon = "T1DaemonID"
            else:  # if event.parametros['charge_daemon'] == "T2DaemonID":
                daemon = "T2DaemonID"
            insert(nodo_info,
                   daemon,   # event.parametros['charge_daemon'],
                   nodo_info.id,
                   nodo_info.id,
                   parametros_envio,
                   event.parametros['prioridad'],
                   event.operacion,  # event.parametros['operacion'],
                   elemento_interno_remitente="t3Daemon",
                   nodo_objetivo=event.parametros['nodo_objetivo']
                   )
        else:
            add_result(self, event.parametros['id_copy'], "Este clon ya se mato,por ordenes de arriba", "t3daemon")

    def kill(self, clone_ID):
        # Debe llevar registro de los clones que mata para que no haga insert
        if clone_ID in self.__clones:
            self.__matar_clon.append(clone_ID)
            self.__clones.remove(clone_ID)
        else:
            pass
            # todo: throw exception.

    def save(self) -> ConcreteMemento:
        # todo: Cuando se modifica el estado?
        self._state = 'state de daemon'
        return ConcreteMemento(self._state)

    def restore(self, memento: Memento):
        self._state = memento.get_state()
        # todo: Igualar todos las propiedades necesarias
