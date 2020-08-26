import copy
import random
# import sys
import pathlib

# todo: Hacer solo los import necesarios
from .auxiliar import encolar, toList
from .daemons import T1Daemon, T2Daemon, T3Daemon
from .salidas import add_all, add_result, regresa, Config
from .elementos import Cliente, Proxy, Buffer, QManager

from .mensajes import *
# Del simulador
from .simulador import Model, Simulation
from .memento import ConcreteMemento, Caretaker, Memento

# Martinez Vargas Edgar Ivan
# 2153043702
""" BabelRemasterChachanga5000
    Sobre topo.txt:
   El nodo 1 se considera como el nodo que hace las peticiones de serivicio (ClientApp).

   Los nodos 2,3,4 se consideran proxies, estan conectados entre si y con el resto de los nodos.
   Los nodos 5,6,7,8 se consideran nodos donde se almacena la informacion. Estos no tienen comunicacion con el nodo 1.

   Es importante tener en cuenta porque al momento de escribir esto, hay numeros magicos que corresponden a la funcion
   de los nodos.

   Sobre la nomenclatura:
   Los nombres de los metodos son herencia directa de los diagramas, con el fin de facilitar la lectura del codigo y
   el entendimiento del sistema/codigo.
   Los nombres y el orden de los parametros tambien son herencia de los diagramas, en medida de lo posible.
   """

"""Constantes del sistema  """
MAX_FAILURES = 1  # Numero de intentos de insert si el resultado de este fue FAILURE_SUSPICION
NUM_COPIES = 3  # Numero de copias creadas por archivo

# Politicas de servicio Qmanager
PRIORIDAD_ALTA = 7
EJECUTA_PRIORIDAD_ALTA = 3
EJECUTA_PRIORIDAD_MEDIA = 1
PRIORIDAD_MEDIA = 2
EJECUTA_PRIORIDAD_BAJA = 1
PRIORIDAD_BAJA = 1

T1_DAEMONS = 5  # Numero de dameons tipo 1
T1_MAX_COUNT = 1  # Numero de intentos del timer t1Daemon

T2_DAEMONS = 5  # Numero de daemon tipo 2

# T3Daemon Solo hay 1 daemon tipo 3
T3_DAEMONS = 1

# Numero de buffers
BUFFERS = 5


class Aleph(Model):

    def __init__(self):
        super().__init__()

        self._state = None

        self.cliente = Cliente()
        self.proxy = Proxy()
        self.qManager = QManager()

        self.buffer = list()
        [self.buffer.append(Buffer(buffer_id)) for buffer_id in range(Config.BUFFERS)]

        self.t1_daemons = list()
        [self.t1_daemons.append(T1Daemon(daemon_id)) for daemon_id in range(Config.T1_DAEMONS)]

        self.t2_daemons = list()
        [self.t2_daemons.append(T2Daemon(daemon_id)) for daemon_id in range(Config.T2_DAEMONS)]

        self.t3_daemons = list()
        [self.t3_daemons.append(T3Daemon(daemon_id)) for daemon_id in range(Config.T3_DAEMONS)]

        # self.buffer = list()
        # [self.buffer.append(buffer_id) for buffer_id in range(BUFFERS)]

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
        """ Funciona como interfaz, manda los mensajes a los elementos del sistema que corresponda. """

        if event.name == "DESPIERTA":
            cliente_do(self)

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


def save_state(self):
    # print()
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
    # TODO: agregar propiedades que faltan
    # print('Estados:', self._state)
    # return ConcreteMemento(self._state)


def restore(self) -> None:
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

    # print(f'My estado cambio ha {self._state}')


# TODO: Hacer de los clientes una clase para poder simular varios


# def save_t1daemons(self):
#     for id_daemon in range(len(self.t1_daemons)):
#         self.caretaker_t1daemons[id_daemon].save()


def cliente_do(self):
    print("Que tipo de accion quieres realizar \n1)Store\n2)Retrieve\n")
    accion = 1
    if accion == 1:
        self.cliente.store(self)


def proxy_do(self, event):
    if event.name == "STORE":
        self.proxy.store(self, event)

    'To ask: Proxy or elsewhere,como lo decidimos '


def buffer_do(self, event):
    # print("##Buffer##")
    if event.source_element == "proxy":
        if event.name == "STORE":
            self.buffer[0].store_from_proxy(self, event)
    # TODO: QUIZA SE PUEDE GENERALIZAR REPORT PARA TODOS LOS TIPOS DE DEMONIOS
    if event.source_element == "t1daemon":
        if event.name == "REPORT":
            self.buffer[0].report_from_t1daemon(self, event)
        if event.name == "STORE":
            self.buffer[0].store_from_t1daemon(self, event)


def qManager_do(self, event):  # QManager
    # Este if esta pensando en la salida de GUI. 
    # if event.parametros != None:
    #     add_result(self, event.parametros['id_copy'] , "##Proxy##")
    # print("########################################################################################## QManager")
    #
    # # Cualquier cosa que le llega, la encola segun su prioridad
    # print("Evento:", event.name)
    # print("Operacion", event.operacion)

    if event.name == "T1DaemonID":
        if event.operacion == "STORE":
            add_result(self, event.parametros['id_copy'], "#QManager#", "qmanager")
            self.qManager.store(self, event, 1)
            save_state(self)
            restore(self)

        if event.operacion == "RETRIEVE":
            print("Ver diagrama Retrieeval process, first phase")
            self.qManager.retrieve_t1daemon()

        if event.operacion == "PROCESS":
            print("Ver diagrama Storage process, last phase/second phase")
        if event.operacion == "ELIMINATECOPY":
            print("Ver diagrama Storage process, second phase")

    if event.name == "T2DaemonID":
        if event.operacion == "STORE":  # Quiza esta demas ?
            print("Ver diagrama Storage process, second phase")

    if event.name == "T3DaemonID":
        if event.operacion == "STORE":
            add_result(self, event.parametros['id_copy'], "Para el T3Daemon", "qmanager")
            self.qManager.store(self, event, 3)

        # ! ESTO DEBERIA DE ESTAR POR SEPARADO, PARA QUE ESTE EN CONTINUA EJECUCION SIN IMPORTAR LOS MENSAJES QUE LE
        # LLEGUEN
        '''
        Politica de Servicio:
            Por cada 3 tareas de alta prioridad se despacha 1 de prioridad Media y
            por cada 2 tareas de priorida media se despacha 1 de prioridad Baja
        '''
    if event.parametros is not None:
        self.qManager.daemon_do(self, event.parametros['id_copy'])
    else:
        self.qManager.daemon_do(self)

    if event.name == "FREE":
        # TODO: A MENOS QUE TODOS ESTEN LIBRES DE NUEVO SE USA EL METODO daemon_do, de otra forma se le asigna el
        self.qManager.free(self, event)
        # TODO: Todos los demonios estan ocupados, entonces nada de lo de arriba se ejecuta, agregar un entra para
        #  cuando llegue el mensaje del demonio cuando se desocupa


# T1Deamon no se activa con mensajes para forzar que se tega que esperar su ejecucion
# Con la finalidad de cumplir con la condicion de que tiene que confirmar la conclusion de su tarea
def t1_Daemon_do(self, event):
    # print("########################################################################################## DEMON 1")
    # print(f'Estos son los parametros:{event.parametros}')
    add_result(self, event.parametros['id_copy'], "##T1Daemon##", "t1daemon")
    # Ver: Que Manager & Type 1 Execution Daemon, with delayed answer
    if event.name == "EXECUTE":
        add_result(self, event.parametros['id_copy'],
                   f'Execute desde T1Daemon {event.target_element_id}', "t1daemon")
        # print("Mando execute desde t1Daemon method", event.target_element_id)
        self.t1_daemons[event.target_element_id].execute(self, event)

    if event.name == "TIMER":
        # print("Timer desde T1Daemon", event.target_element_id)
        add_result(self, event.parametros['id_copy'],
                   f'Timer desde T1Daemon {event.target_element_id}', "t1daemon")
        self.t1_daemons[event.target_element_id].timer(self)

    if event.name == "CONFIRM":
        pass


def t2_Daemon_do(self, event):
    # print("########################################################################################## DEMON 3")
    if event.name == "no me acuerdo we ":
        pass


def t3_Daemon_do(self, event):
    # print("########################################################################################## DEMON 3")
    if event.name == "EXECUTE":
        # print("ESTE ES EL DEMONIO TIPO 3")
        add_result(self, event.parametros['id_copy'], "Este es el T3Daemon: Execute", "t3daemon")
        # print(event.parametros)
        self.t3_daemons[event.target_element_id].execute(self, event)
    if event.name == "TIMER":
        # El parametro event.nodo_objetivo contiene el clone_id
        self.t3_daemons[event.target_element_id].timer(self, event.nodo_objetivo)


def invokeOracle():
    # print("Oracle invocado")
    # ! Numeros magicos!!!!!
    # TODO:Segun topo.txt del nodo 5 al 8 son nodos encargados de almacenar
    return random.randint(5, 8)


# skipcq: PYL-W0613
def generateNewName(file_name):
    return id(file_name)


def waitResult(self):
    pass


def report(self, results):
    print("Reporto los resultados ")
    pass
    # print("                 El resultado de la operacion fue: " + str(self.result))


def update():
    print("Hago update")
    pass


def confirmStorage(self, id_file, id_copy, result):
    # TODO: DEBE DE TENER UN CONTADOR PARA CADA IDFILE DISTINTO, CUANDO LLEGUE RESULTADOS\
    #   LOS ANOTA EN UN CONTADOR, CUANDO EL CONTADOR ESTE  LISTO, CONFIRMA A CLIENTAPP 
    print("Confirmo que ya esta guardado")
    add_result(self, id_copy, "Confirmo que ya esta guardado", "buffer")
    pass


def inicia(lista_fallo=None, tiempo_fallo=None, tiempo_recuperacion=None):
    # import pathlib
    fn = pathlib.Path(__file__).parent / 'topo.txt'

    experiment = Simulation(fn, 500)

    # asocia un pareja proceso/modelo con cada nodo de la grafica
    for i in range(1, len(experiment.graph) + 1):
        m = Aleph()
        experiment.setModel(m, i)
    # print(f'Lista fallo:{lista_fallo}')    
    # print(f'tiempo_fallo{tiempo_fallo}')
    # print(f'tiempore recuperacion{tiempo_recuperacion}')
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
        "DESPIERTA",  # Name
        "",  # operacion
        0.0,  # Time
        1,  # Target
        1,  # Source
        None,  # elemento_interno_objetivo
        None,  # elemento_interno_remitente
        None,  # elem_int_obj_id
        None,  # elem_int_rem_id
        None,  # parametros
        None,  # prioridad
        None,  # nodo_objetivo
        lista_fallo,  # lista_fallo
        tiempo_fallo,  # tiempo_fallo
        tiempo_recuperacion,  # tiempo_recuperacion
        0  # Port=0
    )

    experiment.init(seed)
    experiment.run()

    return regresa()
