# todo: Hacer solo los import necesarios
from back.aleph.daemons.t1daemon import T1Daemon
from back.aleph.daemons.t2daemon import T2Daemon
from back.aleph.daemons.t3daemon import T3Daemon
from back.aleph.elementos.cliente import Cliente
from back.aleph.elementos.proxy import Proxy
from back.aleph.elementos.buffer import Buffer
from back.aleph.elementos.qManager import QManager

from .salidas import add_all, add_result
from .config import Config
from .mensajes import Mensaje
from .memento import Caretaker

# Del simulador
from back.simulador import Model

# Martinez Vargas Edgar Ivan
# 2153043702
""" 
    aleph 
Sobre topo.txt:
    El nodo 1 se considera como el nodo que hace las peticiones de serivicio (ClientApp).
    Los nodos 2,3,4 se consideran proxies, estan conectados entre si, con el cliente y con el resto de los nodos.
    Los nodos 5,6,7,8 se consideran nodos donde se almacena la informacion. Estos no tienen comunicacion con el nodo 1.
    IMPORTANTE!
    Se puede cambiar esta configuracion en salidas.py en la clase Config modificando las constantes:
        NODO_PROXY_LOWER 
        NODO_PROXY_UPPER 
        NODO_SERVER_LOWER 
        NODO_SERVER_UPPER 


Sobre la nomenclatura:
   Los nombres de los metodos que se usan para mandar mensajes, son herencia directa de los diagramas de secuencia, 
   con el fin de facilitar la lectura del codigo y el entendimiento del sistema/codigo.
   Los nombres y el orden de los parametros tambien son herencia de los diagramas, en medida de lo posible.
   
Sobre los nodos: 
    Cada nodo tiene distintos componentes internos : buffer, t1daemon, t2daemon, t3daemon. 
    Para facilitar el uso, todos los nodos tambien tiene componenetes que se manejan como internos pero que realmente 
    no lo son: cliente y proxy.
    Por lo tanto, todos los nodos tiene por lo menos un componente: cliente, proxy, buffer, t1daemon, t2daemon, t3daemon.
    Aunque algunos de estos componentes no se usan. Por ejemplo el nodo 1, es el unico nodo que usara el componente cliente.
   """


class Aleph(Model):
    """
    Se encarga unicamente del manejo y pase de mensajes. Y de guardar y restaurar el estado global del sistema.
    Cada metodo dedicado a un componente interno simplemente llama al componente a hacer alguna operacion segun
    corresponda el mensaje que recibe.
    """

    def __init__(self):
        super().__init__()
        self.tiempo_fallo = None
        self.tiempo_recuperacion = []
        self.estoy_vivo = True
        self.contador_auxiliar = 0

        self._state = None

        self.cliente = Cliente()
        self.proxy = Proxy()
        self.qManager = QManager()

        self.buffer = list()
        for buffer_id in range(Config.BUFFERS):
            self.buffer.append(Buffer(buffer_id))

        self.t1_daemons = list()
        for daemon_id in range(Config.T1_DAEMONS):
            self.t1_daemons.append(T1Daemon(daemon_id))

        self.t2_daemons = list()
        for daemon_id in range(Config.T2_DAEMONS):
            self.t2_daemons.append(T2Daemon(daemon_id))

        self.t3_daemons = list()
        for daemon_id in range(Config.T3_DAEMONS):
            self.t3_daemons.append(T3Daemon(daemon_id))

        self.id_nodos = []  # Guarda el id del nodo que hizo la operacion de store de forma exitosa
        self.target_status = "ok"

        self.caretaker_cliente = Caretaker(self.cliente)
        self.caretaker_proxy = Caretaker(self.proxy)
        self.caretaker_qmanager = Caretaker(self.qManager)

        self.caretakers_t1daemon = list()
        [self.caretakers_t1daemon.append(Caretaker(self.t1_daemons[daemon_id]))
         for daemon_id in range(len(self.t1_daemons))]

        self.caretakers_t2daemon = list()
        [self.caretakers_t2daemon.append(Caretaker(self.t2_daemons[daemon_id]))
         for daemon_id in range(len(self.t2_daemons))]

        self.caretakers_t3daemon = list()
        [self.caretakers_t3daemon.append(Caretaker(self.t3_daemons[daemon_id]))
         for daemon_id in range(len(self.t3_daemons))]

        self.caretakers_buffer = list()
        [self.caretakers_buffer.append(Caretaker(self.buffer[buffer_id]))
         for buffer_id in range(len(self.buffer))]

        self.snapshot = None

    def receive(self, event):
        """
        Funciona como interfaz, manda los mensajes a los elementos del sistema que corresponda.
            Y maneja la simulacion del fallo con su recuperacion.
        """

        if event.name == "AVISO_FALLO":
            """
            Al inicio del algoritmo se manda un mensaje a los nodos que van a fallar con la informacion necesaria para 
            simular su fallo.
            """
            if self.id in event.lista_fallo:
                # Un nodo puede fallar mas de una vez, se busca en la lista.
                indexes = [i for i, x in enumerate(event.lista_fallo) if x == self.id]
                for i in indexes:
                    newevent = Mensaje("FALLO", self.clock + event.tiempo_fallo[i], self.id, self.id)
                    self.transmit(newevent)
                    self.tiempo_recuperacion.append(event.tiempo_recuperacion[i])

        if event.name == "FALLO":
            # Se crea el snapshot del sistema y se entra en fallo
            save_state(self)
            self.estoy_vivo = False
            add_all(self,
                    f"Entrando en fallo, me voy a recuperar en el tiempo{self.clock + self.tiempo_recuperacion[self.contador_auxiliar]}")
            print(
                f"Nodo: {self.id} Entro en Fallo. Me voy a recuperar en {self.tiempo_recuperacion[self.contador_auxiliar]}")
            newevent = Mensaje("RECUPERA", self.clock + self.tiempo_recuperacion[self.contador_auxiliar], self.id,
                               self.id)
            self.transmit(newevent)
            self.contador_auxiliar += 1

        if self.estoy_vivo:
            if event.name == "DESPIERTA" or event.target_element == "cliente":
                cliente_do(self, event)

            if event.target_element == "proxy":
                proxy_do(self, event)

            if event.target_element == "buffer":
                buffer_do(self, event)

            if event.target_element == "qmanager":
                qManager_do(self, event)

            if event.target_element == "t1daemon":
                t1_Daemon_do(self, event)

            if event.target_element == "t2daemon":
                t2_Daemon_do(self, event)

            if event.target_element == "t3daemon":
                t3_Daemon_do(self, event)
        else:
            if event.name == "RECUPERA":
                print(f"Nodo:{self.id} Ya me recupere compa")
                add_all(self, f"Ya me recupere c:")
                self.estoy_vivo = True
                restore_state(self)


def save_state(self):
    """
    Cada objeto dentro del nodo se encarga de guardar su propio estado.
    Unicamente el objeto tiene acceso a su propio snapshot.
    Ver documentacion sobre memento para mas informacion
    """
    # for daemon in range(len(self.caretakers_t1daemon)):
    #     self.caretakers_t1daemon[daemon].save()

    # for daemon in range(len(self.caretakers_t2daemon)):
    #     self.caretakers_t2daemon[daemon].save()

    # for daemon in range(len(self.caretakers_t3daemon)):
    #     self.caretakers_t3daemon[daemon].save()

    # for buffer in range(len(self.caretakers_buffer)):
    #     self.caretakers_buffer[buffer].save()

    # self.caretaker_cliente.save()
    # self.caretaker_proxy.save()
    self.caretaker_qmanager.save()

    # Para los elementos propios no se usa el patron memento
    # self.snapshot = {'prueba': self.prueba}

    # TODO: agregar propiedades que faltan


def restore_state(self) -> None:
    """
    Como solamente cada objeto tiene acceso a su memento y su propio estado,
    cada quien se restaura por si mismo.
    """
    # self.caretaker_cliente.restore()
    # self.caretaker_proxy.restore()
    self.caretaker_qmanager.restore()
    # for buffer_id in range(len(self.caretakers_buffer)):
    #     self.caretakers_buffer[buffer_id].restore()

    # for daemons in range(len(self.caretakers_t1daemon)):
    #     self.caretakers_t1daemon[daemons].restore()
    # for daemons in range(len(self.caretakers_t2daemon)):
    #     self.caretakers_t2daemon[daemons].restore()
    # for daemons in range(len(self.caretakers_t3daemon)):
    #     self.caretakers_t3daemon[daemons].restore()
    # self.prueba = self.snapshot['prueba']
    self.snapshot.clear()


def cliente_do(self, event):
    if event.name == "DESPIERTA":
        print("Que tipo de accion quieres realizar \n1)Store\n2)Retrieve\n")
        accion = 1
        if accion == 1:
            self.cliente.store(self)
    if event.name == "CONFIRM":
        self.cliente.confirm(self, event)


def proxy_do(self, event):
    if event.name == "STORE":
        self.proxy.store(self, event)
    if event.name == "CONFIRM":
        self.proxy.confirm(self, event)

    'To ask: Proxy or elsewhere,como lo decidimos '


def buffer_do(self, event):
    if event.source_element == "proxy":
        if event.name == "STORE":
            self.buffer[0].store_from_proxy(self, event)
    # TODO: QUIZA SE PUEDE GENERALIZAR REPORT PARA TODOS LOS TIPOS DE DEMONIOS
    if event.source_element == "t1daemon":
        if event.name == "SUCESS" or event.name == "FAILURE":
            self.buffer[0].report_from_t1daemon(self, event)
        if event.name == "TASK":
            if event.operacion == "STORE":
                self.buffer[0].store_from_t1daemon(self, event)
            elif event.operacion == "PROCESS":
                self.buffer[0].process(self, event)
    if event.source_element == "t2daemon":
        if event.name == "TASK":
            if event.operacion == "STORE_DISPERSO":
                self.buffer[0].store_from_t2daemon(self, event)

        if event.name == "CONFIRM":
            self.buffer[event.source_element_id].confirm(self, event)


def qManager_do(self, event):  # QManager
    """
    Politica de Servicio:
        Por cada 3 tareas de alta prioridad se despacha 1 de prioridad Media y
        por cada 2 tareas de priorida media se despacha 1 de prioridad Baja
    """
    if event.name == "T1DaemonID":
        if event.operacion == "STORE":
            self.qManager.store(self, event, 1)

        if event.operacion == "RETRIEVE":
            print("Ver diagrama Retrieeval process, first phase")
            self.qManager.retrieve_t1daemon()

        if event.operacion == "PROCESS":
            self.qManager.store(self, event, 1)
            print("###########Ver diagrama Storage process, last phase/second phase")
        if event.operacion == "ELIMINATECOPY":
            print("Ver diagrama Storage process, second phase")

    if event.name == "T2DaemonID":
        if event.operacion == "STORE":  # todo: Quiza esta demas ?
            self.qManager.store(self, event, 2)
            # print("Ver diagrama Storage process, second phase")

    if event.name == "T3DaemonID":
        if event.operacion == "STORE":
            add_result(self, event.parametros['id_copy'], "Para el T3Daemon", "qmanager")
            self.qManager.store(self, event, 3)

        # ! ESTO DEBERIA DE ESTAR POR SEPARADO, PARA QUE ESTE EN CONTINUA EJECUCION SIN IMPORTAR LOS MENSAJES QUE LE
        # LLEGUEN

    # Se encarga de desencolar operaciones siempre que sea posible
    if 'id_copy' in event.parametros:
        self.qManager.daemon_do(self, event.parametros['id_copy'])
    elif event.name != 'FREE':
        print(f"FALLO:{event.name}, OPERACION: {event.operacion}, source:{event.source}, a quien soy: {self.id}")
        self.qManager.daemon_do(self)

    if event.name == "FREE":
        # TODO: Daemon do que vaya dirigido solo a ese deamon sin tener que hacer todo lo demas
        self.qManager.daemon_do(self, event.parametros['id_copy'])


def t1_Daemon_do(self, event):
    add_result(self, event.parametros['id_copy'], f"##T1Daemon##", "t1daemon")
    # Ver: Que Manager & Type 1 Execution Daemon, with delayed answer
    if event.name == "EXECUTE":
        self.t1_daemons[event.target_element_id].execute(self, event)

    if event.name == "TIMER":
        self.t1_daemons[event.target_element_id].timer(self, event)

    if event.name == "CONFIRM":
        self.t1_daemons[event.target_element_id].confirm(self, event)
        pass


def t2_Daemon_do(self, event):
    add_result(self, event.parametros['id_copy'], "##T2Daemon", "t2daemon")
    if event.name == "EXECUTE":
        self.t2_daemons[event.target_element_id].execute(self, event)
    if event.name == "CONFIRM":
        self.t2_daemons[event.target_element_id].confirm(self, event)
    if event.name == "TIMER":
        self.t2_daemons[event.target_element_id].timer(self, event)


def t3_Daemon_do(self, event):
    if event.name == "EXECUTE":
        add_result(self, event.parametros['id_copy'], "Este es el T3Daemon: Execute", "t3daemon")
        self.t3_daemons[event.target_element_id].execute(self, event)
    if event.name == "TIMER_CLONE":
        self.t3_daemons[event.target_element_id].timer(self, event)
    if event.name == "KILL":
        self.t3_daemons[event.target_element_id].kill(self, event)  # Parametros es el clone id
