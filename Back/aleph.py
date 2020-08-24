from .daemons import T1Daemon, T2Daemon, T3Daemon
from .salidas import Config
from .memento import Memento, ConcreteMemento, Carataker


class Aleph():
    def __init(self):
        self._state = None
        self._estoy_activo = True

        self.t1_daemons = list()
        [self.t1_daemons.append(T1Daemon(daemon_id)) for daemon_id in range(Config.T1_DAEMONS)]

        self.t2_daemons = list()
        [self.t2_daemons.append(T2Daemon(daemon_id)) for daemon_id in range(Config.T2_DAEMONS)]

        self.t3_daemons = list()
        [self.t3_daemons.append(T3Daemon(daemon_id)) for daemon_id in range(Config.T3_DAEMONS)]

        self.buffer = list()
        [self.buffer.append(buffer_id) for buffer_id in range(Config.BUFFERS)]

        self.target_status = "ok"
        self.wait_status = False
        self.politica = "HIGH"
        self.status_daemons = [True, True, True]

        self.id_nodos = []  # Guarda el id del nodo que hizo la operacion de store de forma exitosa

        # QManager
        self.queue_high = [[] for __ in range(0)]
        self.queue_medium = [[] for __ in range(0)]
        self.queue_low = [[] for __ in range(0)]

        # Contador para politicas de servicio
        self.cont_prioridad_alta = 0
        self.cont_prioridad_media = 0
        self.cont_prioridad_baja = 0

    def proxy_do(self, event):
        pass

    def buffer_do(self, event):
        pass

    def qmanager_do(self, event):
        pass

    def t1_daemon(self, event):
        pass

    def t2_daemon(self, event):
        pass

    def t3_daemon(self, event):
        pass

    def save(self):
        # State tiene que ser aquello que nos ayude a 
        # resturar el estado, quiza una lista o diccionario

        return ConcreteMemento(self._state)

    def restore(self, memento):
        # Aqui voy a restaurar todos los valores que obtenga del memento 
        # Quiza tenga que igualar muchas cosas
        self._state = memento.get_state()
