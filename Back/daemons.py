# from StorageProcessMsg import T1_TIMER_STATE
from .mensajes import *
from .salidas import add_result, add_all, Config
from .memento import ConcreteMemento, Caretaker, Memento

import copy
import uuid

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
        self.results = list()
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
                       self.daemon_id,
                       "t1daemon"
                       )
            startTimer(nodo_info,
                       parametros,  # Incluye ahora timer_state
                       event.operacion,
                       self.daemon_id,
                       event.nodo_objetivo,
                       event.prioridad,
                       "t1daemon"
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
                       daemon_id=self.daemon_id
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
        add_result(nodo_info, event.parametros['id_copy'],
                   f"T1Daemon:{self.daemon_id}: Llego confirmacion de la operacion desde nodo:{event.source}, Mando "
                   f"report", "t1daemon")
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
        self.results = list()
        self.clones_pendientes = list()
        self.id_operacion = 0

    def execute(self, nodo_info, event):
        add_result(nodo_info, event.parametros['id_copy'],
                   f'Execute desde T2Daemon {event.target_element_id}', "t2daemon")
        self.status = "BUSY"
        # invokeOracle() le regresa el estado del nodo segun el HBManager, aqui supondremos que siempre lo manda
        parametros = copy.copy(event.parametros)
        if parametros['taskReplica'] == 0:
            # Solo entra aqui la primera vez
            parametros['taskReplica'] = 1
            parametros['id_operacion_t2daemon'] = self.id_operacion
            self.id_operacion += 1
            self.results.append('FALSE')
            print(f"Nodo:{nodo_info.id} t2Daemon creando t3Daemon, le mando mi {self.daemon_id}")
            parametros['id_clone'] = uuid.uuid4()
            self.clones_pendientes.append(parametros['id_clone'])
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
            print(
                "Ya se habia eliminado este clon, quiza el t3 estaba en fallo cuando se le mando la intruccion de eliminar")
            # ! IMPORTANTE, COMO AUN NO ELIMINA EL CLON, PUEDE QUE SALGA MUCHO ESTO.

    def timer(self, nodo_info, event):
        add_result(nodo_info, event.parametros['id_copy'], "Timer T2 Daemon, se hace insert", "t2daemon")
        # LLego resultado
        if self.results[event.parametros['id_operacion_t2daemon']]:
            add_result(nodo_info, event.parametros['id_copy'],
                       "LLego la respuesta antes de expirar el timer, tengo que matrar clon", "t2daemon")
            print(f"Nodo:{nodo_info.id} T2Daemon {self.daemon_id}: Ya llego la respuesta, tengo que matar al clon")
            kill_clone(nodo_info, event.parametros['id_clone'], "t2daemon", self.daemon_id)
            try:
                print(f"T2Daemon:{self.daemon_id} Estoy eliminando el clon {event.parametros['id_clone']} de mis registros")
                self.clones_pendientes.remove(event.parametros['id_clone'])
            except ValueError:
                print(f"Nodo:{nodo_info.id}. T2Daemon: {self.daemon_id}. Ya se habia eliminado este clon.")
        else:
            add_result(nodo_info, event.parametros['id_copy'], "No ha llegado la respuesta, hago insert", "t2daemon")
            print(f"Nodo:{nodo_info.id} T2Daemon: No ha llegado la respuesta, hago insert")
            event.parametros['taskReplica'] += 1
            insert(nodo_info,
                   "T2DaemonID",
                   nodo_info.id,
                   nodo_info.id,
                   event.parametros,
                   event.prioridad,
                   event.operacion,
                   elemento_interno_remitente="t2daemon",
                   nodo_objetivo=event.parametros['nodo_objetivo'],
                   # elemento_interno_id=self.daemon_id,
                   daemon_id=self.daemon_id
                   )
        self.status = "FREE"

    def confirm(self, nodo_info, event):
        add_result(nodo_info, event.parametros['id_copy'], "Llego confirmacion", "t2daemon")

        pass

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
        self.__matar_clon = list()
        # self.__parametros = None

    def execute(self, nodo_info, event):
        parametros = copy.copy(event.parametros)
        add_result(nodo_info, parametros['id_copy'], "Execute Daemon 3, inicio timer", "t3daemon")
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
        add_result(nodo_info, event.parametros['id_copy'], "Timer de T3Daemon", "t3daemon")
        # TODO: Este if esta mal. El id del clon es parametros['clone_id], pero primero se tiene que asegurar que viene del mismo nodo
        if event.parametros['id_clone'] in self.__clones:
            add_result(nodo_info, event.parametros['id_copy'], "Mando insert", "t3daemon")
            if event.parametros['charge_daemon'] == "t1daemon":
                daemon = "T1DaemonID"
            else:  # if event.parametros['charge_daemon'] == "T2DaemonID":
                daemon = "T2DaemonID"
                print(f"Nodo: {nodo_info.id}. Soy t3Daemon, creo t2daemo{event.parametros['source_id']}, "
                      f"no deberia estar en: {event.parametros['nodo_objetivo']}")

            insert(nodo_info,
                   daemon,  # event.parametros['charge_daemon'],
                   nodo_info.id,
                   nodo_info.id,
                   event.parametros,
                   event.parametros['prioridad'],
                   event.operacion,
                   elemento_interno_remitente="t3Daemon",
                   nodo_objetivo=event.parametros['nodo_objetivo'],
                   # elemento_interno_id=event.parametros['source_id'],
                   daemon_id=event.parametros['source_id']
                   )
        else:
            print("!!!!!Este clon ya se mato, por ordenes de arriba")
            add_result(nodo_info, event.parametros['id_copy'], "Este clon ya se mato,por ordenes de arriba", "t3daemon")

    def kill(self, nodo_info, id_clone):
        if id_clone in self.__clones:
            print("Este clon se muere. Tengo vigote")
            self.__clones.remove(id_clone)
        else:
            print(f"No esta el clon {nodo_info} que deseas eliminar, esta en otro nodo o alguien mas ya lo elimino")


    def save(self) -> ConcreteMemento:
        # todo: Cuando se modifica el estado?
        self._state = 'state de daemon'
        return ConcreteMemento(self._state)

    def restore(self, memento: Memento):
        self._state = memento.get_state()
        # todo: Igualar todos las propiedades necesarias
