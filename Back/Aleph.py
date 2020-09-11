import random
import pathlib

# todo: Hacer solo los import necesarios
from .auxiliar import encolar, toList
from .daemons import T1Daemon, T2Daemon, T3Daemon
from .salidas import add_all, add_result, regresa, Config
from .elementos import Cliente, Proxy, Buffer, QManager
from .mensajes import Mensaje
# Del simulador
from .simulador import Model, Simulation
from .memento import ConcreteMemento, Caretaker, Memento

# Martinez Vargas Edgar Ivan
# 2153043702
""" 
    Aleph 
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
        self.tiempo_recuperacion = None
        self.estoy_vivo = True

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
        # QManager

    def receive(self, event):
        """ Funciona como interfaz, manda los mensajes a los elementos del sistema que corresponda.
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
                    # newevent2 = Mensaje("RECUPERA", self.clock+event.tiempo_recuperacion[i], self.id, self.id)
                    # self.transmit(newevent2)

        if event.name == "FALLO":
            # Se crea el snapshot del sistema y se entra en fallo
            save_state(self)
            self.estoy_vivo = False

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
                self.estoy_vivo = True
                restore(self)


def save_state(self):
    """
    Cada objeto dentro del nodo se encarga de guardar su propio estado.
    Unicamente el objeto tiene acceso a su propio snapshot.
    Ver documentacion sobre memento para mas informacion
    """
    self._state = {
        'cliente': self.caretaker_cliente.save(),
        'proxy': self.caretaker_proxy.save(),
        'qmanager': self.caretaker_qmanager.save(),
        'buffer': [
            self.caretakers_buffer[buffer_id].save()
            for buffer_id in range(len(self.buffer))
        ],
        't1_daemon': [
            self.caretakers_t1daemon[id_daemon].save()
            for id_daemon in range(len(self.t1_daemons))
        ],
        't2_daemon': [
            self.caretakers_t2daemon[id_daemon].save()
            for id_daemon in range(len(self.t2_daemons))
        ],
        't3_daemon': [
            self.caretakers_t3daemon[id_daemon].save()
            for id_daemon in range(len(self.t3_daemons))
        ]
    }
    # TODO: Quiza no necesite guardar los caretaker.save en self._state
    # TODO: agregar propiedades que faltan


def restore(self) -> None:
    """
    Como solamente cada objeto tiene acceso a su memento y su propio estado,
    cada quien se restaura por si mismo.
    """
    self.caretaker_cliente.restore()
    self.caretaker_proxy.restore()
    self.caretaker_qmanager.restore()
    for buffer_id in range(len(self.buffer)):
        self.caretakers_buffer[buffer_id].restore()

    for daemons in range(len(self.t1_daemons)):
        self.caretakers_t1daemon[daemons].restore()
    for daemons in range(len(self.t2_daemons)):
        self.caretakers_t2daemon[daemons].restore()
    for daemons in range(len(self.t3_daemons)):
        self.caretakers_t3daemon[daemons].restore()


def cliente_do(self, event):
    if event.name == "DESPIERTA":
        print("Que tipo de accion quieres realizar \n1)Store\n2)Retrieve\n")
        accion = 1
        if accion == 1:
            self.cliente.store(self)
    if event.name == "CONFIRM":
        print("CONFIRM A CLIENT")
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
        if event.name == "STORE":
            self.buffer[0].store_from_t1daemon(self, event)


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
            print("Ver diagrama Storage process, last phase/second phase")
        if event.operacion == "ELIMINATECOPY":
            print("Ver diagrama Storage process, second phase")

    if event.name == "T2DaemonID":
        if event.operacion == "STORE":  #todo: Quiza esta demas ?
            self.qManager.store(self, event, 2)
            # print("Ver diagrama Storage process, second phase")

    if event.name == "T3DaemonID":
        if event.operacion == "STORE":
            add_result(self, event.parametros['id_copy'], "Para el T3Daemon", "qmanager")
            self.qManager.store(self, event, 3)

        # ! ESTO DEBERIA DE ESTAR POR SEPARADO, PARA QUE ESTE EN CONTINUA EJECUCION SIN IMPORTAR LOS MENSAJES QUE LE
        # LLEGUEN

    # Se encarga de desencolar operaciones siempre que sea posible
    if event.parametros is not None:
        self.qManager.daemon_do(self, event.parametros['id_copy'])
    else:
        self.qManager.daemon_do(self)

    if event.name == "FREE":
        # TODO: A MENOS QUE TODOS ESTEN LIBRES DE NUEVO SE USA EL METODO daemon_do, de otra forma se le asigna el
        self.qManager.free(self, event)


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


def t3_Daemon_do(self, event):
    if event.name == "EXECUTE":
        add_result(self, event.parametros['id_copy'], "Este es el T3Daemon: Execute", "t3daemon")
        self.t3_daemons[event.target_element_id].execute(self, event)
    if event.name == "TIMER_CLONE":
        # El parametro event.nodo_objetivo contiene el clone_id
        self.t3_daemons[event.target_element_id].timer(self, event.nodo_objetivo, event)


# Main
def inicia(lista_fallo=None, tiempo_fallo=None, tiempo_recuperacion=None):
    """
    Se llama desde app/auth/views.py
    Se hace la validacion de lista_fallo, tiempo_fallo y tiempo_recuperacion para que
    las 3 listas esten completamente vacias o las 3 listas contengan datos.
    """
    fn = pathlib.Path(__file__).parent / 'topo.txt'
    experiment = Simulation(fn, 500)
    # asocia un pareja proceso/modelo con cada nodo de la grafica
    for i in range(1, len(experiment.graph) + 1):
        m = Aleph()
        experiment.setModel(m, i)

    # ! No es necesrio hacer los 3 ifs porque desde el GUI se valida.
    # Si uno esta vacia todos lo estan, si una tine cosas, las demas tambien.
    if lista_fallo.strip():
        lista_fallo = toList(lista_fallo, "int")
        print(f'Esta es la lista: {lista_fallo}')
    if tiempo_fallo.strip():
        tiempo_fallo = toList(tiempo_fallo, 'float')
        print(f'Estos son los tiempo de fallo {tiempo_fallo}')
    if tiempo_recuperacion.strip():
        tiempo_recuperacion = toList(tiempo_recuperacion, 'float')
        print(f'Estos son los tiempos de recuperacion {tiempo_recuperacion}')

    # inserta un evento semilla en la agenda y arranca
    seed = Mensaje(
        "DESPIERTA",
        0.0,  # Tiempo
        1,  # Target
        1,  # Source
        lista_fallo=lista_fallo,
        tiempo_fallo=tiempo_fallo,
        tiempo_recuperacion=tiempo_recuperacion
    )
    experiment.init(seed)
    if lista_fallo.strip():
        seed_all(experiment,
                 experiment.numero_nodos,
                 "AVISO_FALLO",
                 lista_fallo,
                 tiempo_fallo,
                 tiempo_recuperacion)
    experiment.run()

    return regresa()


def seed_all(experiment: Simulation, numero_nodos: int, mensaje: str,
             lista_fallo: list, tiempo_fallo: list, tiempo_recuperacion: list):
    """
    Genera semillas. En este caso manda a los nodos que van a fallar la informacion que necesitan para
    simular el fallo y la recuperacion. Si se quita el if, se puede ver como una especie de broadcast
    """
    for nodo in range(1, numero_nodos + 1):
        if nodo in lista_fallo:
            seed = Mensaje(mensaje, 0.0, nodo, nodo,
                           lista_fallo=lista_fallo,
                           tiempo_fallo=tiempo_fallo,
                           tiempo_recuperacion=tiempo_recuperacion)
            experiment.init(seed)
