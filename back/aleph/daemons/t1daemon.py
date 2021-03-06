import copy

from back.aleph.daemons import Daemon
from back.aleph.mensajes import report, invokeTask, startTimer, insert, mensajeDaemon
from back.aleph.salidas import add_result
from back.aleph.config import Config
from back.aleph.memento import ConcreteMemento, Memento


class T1Daemon(Daemon):
    def __init__(self, daemon_id, status="FREE"):
        Daemon.__init__(self, daemon_id, status)
        self._state = None
        # self.__status = None
        self.results = []
        self.__id_operacion = 0

    # @staticmethod
    def execute(self, nodo_info, event):
        # add_result(nodo_info, event.parametros['id_copy'],
        #            f'Execute desde T1Daemon {event.target_element_id}', "t1daemon")
        if nodo_info.target_status == "suspected":
            add_result(nodo_info, event.parametros['id_file'],
                       f"ID:{self.daemon_id} Target is suspected.", "t1daemon")
            report(self,
                   "FAILURE",
                   self.daemon_id,
                   event.parametros,
                   event.prioridad,
                   event.operacion,
                   event.nodo_objetivo)
        else:  # Target is supposed to be ok
            self.status = "BUSY"
            parametros = copy.copy(event.parametros)
            if 'timer_state' not in parametros:
                parametros['timer_state'] = 0
                parametros['id_operacion'] = self.__id_operacion
                self.__id_operacion += 1
                self.results.append('FALSE')
            # self.__timer_state = parametros['timer_state']
            add_result(nodo_info, event.parametros['id_copy'],
                       f"ID:{self.daemon_id} Mando operacion:{event.operacion} a nodo objetivo:{event.nodo_objetivo} y programo timer",
                       "t1daemon")
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

    def timer(self, nodo_info, event):
        """Utiliza nodo_info para obtener la informacion del nodo donde vive, como el id y el clock """
        add_result(nodo_info, event.parametros['id_copy'],
                   f'ID:{self.daemon_id} Timer expirado.', "t1daemon")
        parametros = copy.copy(event.parametros)
        index_operacion = event.parametros["id_operacion"]
        if self.results[index_operacion] is True:
            # Ya llego la confirmacion de que la tarea se completo, el daemon queda libre y se tiene que limpiar
            # los atributos para futuros usos distintos a storage
            add_result(nodo_info, event.parametros['id_copy'],
                       f"ID:{self.daemon_id} Ya habia llegado el resultado, se ignora el timer.",
                       "t1daemon")
        else:
            if parametros['timer_state'] < Config.T1_TIMER_STATE:
                parametros["timer_state"] += 1
                add_result(nodo_info, parametros['id_copy'],
                           f"Intento de nuevo, pues no recibi respuesta de nodo objetivo:{event.nodo_objetivo}",
                           "t1daemon")
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
                add_result(nodo_info, parametros['id_copy'], f"ID:{self.daemon_id} Numero de intentos sobrepasado"
                                                             f". Reportamos Failure", "t1daemon")
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
        self.status = "FREE"
        mensajeDaemon(nodo_info, "FREE", self.daemon_id, "t1daemon", "1", event.parametros['id_copy'])

    def confirm(self, nodo_info, event):
        """
        Cuando llega una confirmacion del nodo a quien se le mando el trabajo, manda el report con SUCESS \n
        No le importa el estado del timer. Pero con self.results le avisa al timer
        """
        index_operacion = event.parametros["id_operacion"]
        self.results[index_operacion] = True

        if event.operacion == "Creacion Clon":
            add_result(nodo_info, event.parametros['id_copy'],
                       f"ID:{self.daemon_id} Confirmacion. Nodo {event.source},creo clon. No reporto a Proxy",
                       "t1daemon")
        elif event.operacion == "Ya despachado":
            add_result(nodo_info, event.parametros['id_copy'], f"ID:{self.daemon_id}. "
                                                               f"Confirmacion. Nodo {event.source} ya habia procesado la operacion",
                       "t1daemon")
        elif event.operacion == "Procesamiento":
            add_result(nodo_info, event.parametros['id_copy'], f"ID:{self.daemon_id}"
                                                               f"Confirmacion. Nodo {event.source} proceso el archivo {event.parametros['id_file']}",
                       "t1daemon")
        else:
            add_result(nodo_info, event.parametros['id_copy'],
                       f"ID:{self.daemon_id}. Confirmacion. Nodo:{event.source}, "
                       f"Mando report", "t1daemon")
            report(nodo_info, "SUCESS", self.daemon_id, event.parametros, event.nodo_objetivo,
                   operacion=event.operacion)

    def save(self) -> ConcreteMemento:
        # todo: Cuando se modifica el estado?
        self._state = 'state de daemon'
        print(f"SOY T1 DAMEON ESTE ES MI STATE: {self._state}: {self.daemon_id}")
        return ConcreteMemento(self._state)

    def restore(self, memento: Memento):
        self._state = memento.get_state()
        # todo: Igualar todos las propiedades necesarias
