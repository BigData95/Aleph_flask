# from StorageProcessMsg import T1_TIMER_STATE
from .mensajes import *
from .salidas import add_result, add_all
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
    def __init__(self, __daemon_id, __status="FREE"):
        Daemon.__init__(self, __daemon_id, __status)
        self._state = None
        self.__nodo_objetivo = None
        self.__status = None
        self.__operacion = None
        self.__prioridad = None
        self.__timer_state = 0
        self.__parametros = None
        self.result = True  # False  # Sabe si ya tiene el resultado o no

    # @staticmethod
    def execute(self, nodo_info, event):
        if nodo_info.target_status == "suspected":
            report(self, "FAILURE", self.__daemon_id)  
        else:# Target is supposed to be ok
            # self.result = False
            self.__status = "BUSY"
            self.__parametros = event.parametros
            self.__nodo_objetivo = event.nodo_objetivo
            self.__operacion = event.operacion
            self.__prioridad = event.prioridad
            if not 'timer_state' in self.__parametros:
                self.__parametros['timer_state'] = 0
            self.__timer_state = self.__parametros['timer_state']
            add_result(nodo_info, event.parametros['id_copy'], "t1Class: Mando Invoketask", "t1daemon")
            parametros_envio = {
                'file': self.__parametros['file'],
                'id_file': self.__parametros['id_file'],
                'id_copy': self.__parametros['id_copy']
            }
            invokeTask(nodo_info,
                    self.__nodo_objetivo,
                    self.__operacion,  
                    parametros_envio,
                    self.daemon_id
                    )
            startTimer(nodo_info,
                    {'id_copy': event.parametros['id_copy']},  # Para poder imprimir en GUI 
                    self.daemon_id,
                    self.daemon_id)  # TODO: Agregar la variable del timer
            add_result(nodo_info, event.parametros['id_copy'], "t1Class: Mando Timer", "t1daemon")


    def timer(self, nodo_info):
        """Utiliza nodo_info para obtener la informacion del nodo donde vive, como el id y el clock """
        if self.result:
            # print("Ya llego la confirmacion, la mandamos SUCESS")
            add_result(nodo_info, self.__parametros['id_copy'], "LLego confirmacion, mandomos SUCESS", "t1daemon")
            # print("Estos son los parametros!", self.__parametros)
            self.__parametros["reported"] += 1  # Se hace desde aqui , no desde el buffer
            report(nodo_info, "SUCESS", self.daemon_id, self.__parametros)
        # TODO: NO OLVIDAR CAMBIAR RESULT A FALSE o cambiar en execute(?) esta en sucess para pruebas
        else:
            if self.__timer_state < T1_TIMER_STATE:
                self.__parametros["timer_state"] = self.__timer_state + 1
                # print("Hago insert porque no recibi repuesta")
                add_result(nodo_info, self.__parametros['id_copy'], "Hago insert pues no recibi respuesta", "t1daemon")
                insert(nodo_info,
                       "T1DaemonID",
                       nodo_info.id,
                       nodo_info.id,
                       self.__parametros,
                       self.__prioridad,
                       self.__operacion,
                       self.__nodo_objetivo
                       )
            else:
                # print("Debemos reportar la falla")
                add_result(self, self.__parametros['id_copy'], "Debemos reportar la falla", "t1daemon")
                self.__parametros["reported"] += 1
                # print("PARAMETROS QUE ENVIO:", self.__parametros)
                report(nodo_info,
                       "FAILURE",
                       self.daemon_id,
                       self.__parametros,
                       self.__prioridad,
                       self.__operacion,
                       self.__nodo_objetivo
                       )
            # TODO: NO OLVIDAR CAMBIAR RESULT A FALSE
        # Aviso que ya estoy disponible
        self.__status = "FREE"
        mensajeDaemon(nodo_info, "FREE", self.daemon_id, "1")


    def confirm(self, nodo_info):
        print("Confirmacion")
        pass

    def save(self) -> ConcreteMemento:
        # todo: Cuando se modifica el estado?
        self._state = 'state de daemon'
        print(f"SOY T1 DAMEON ESTE ES MI STATE: {self._state}: {self.daemon_id}")
        return ConcreteMemento(self._state)

    def restore(self, memento: Memento):
        self._state = memento.get_state()
        # todo: Igualar todos las propiedades necesarias


class T2Daemon(Daemon):
    def __init__(self, __daemon_id, __status="FREE"):
        super().__init__(__daemon_id, __status)
        self._state = None

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
        self.__clon_id = 0
        self.__clones = list()
        self.__matar_clon = list()
        self.__parametros = None

    def execute(self, nodo_info, event):
        self.__parametros = copy.copy(event.parametros)
        self.__parametros['operacion'] = event.operacion
        self.__parametros['prioridad'] = event.prioridad
        self.__parametros['nodo_objetivo'] = event.nodo_objetivo
        # print("Execute daemon 3")
        add_result(nodo_info, self.__parametros['id_copy'], "Execute Daemon 3", "t3daemon")
        # print(self.__parametros)
        startTimerClone(nodo_info,
                        event.parametros['timer'],
                        event.parametros['tipo_daemon'],
                        self.__clon_id, self.daemon_id
                        )
        self.__clones.append(self.__clon_id)
        self.__clon_id += 1

    def timer(self, nodo_info, nodo_id):
        # print("Timer de T3Daemon")
        add_result(nodo_info, self.__parametros['id_copy'], "Timer de T3Daemon", "t3daemon")
        if not nodo_id in self.__matar_clon:
            # Para t1Daemon
            parametros_envio = {
                'file': self.__parametros['file'],
                'id_file': self.__parametros['id_file'],
                'id_copy': self.__parametros['id_copy'],
                'reported': 0
            }
            # print("Mando insert")
            add_result(nodo_info, self.__parametros['id_copy'], "Mando insert", "t3daemon")
            insert(nodo_info,
                   self.__parametros['tipo_daemon'],
                   nodo_info.id,
                   nodo_info.id,
                   parametros_envio,
                   self.__parametros['prioridad'],
                   self.__parametros['operacion'],
                   elemento_interno_remitente="t3Daemon",
                   nodo_objetivo=self.__parametros['nodo_objetivo']
                   )
        else:
            # print("Este clon ya se mato, por ordenenes de arriba")
            add_result(self, self.__parametros['id_copy'], "Este clon ya se mato,por ordenes de arriba", "t3daemon")

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
