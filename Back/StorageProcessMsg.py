import copy
import random
import sys

from .auxiliar import *
from .daemons import *

from .simulador import Model, Simulation


# from model import Model

# from simulation import Simulation

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

# T1Daemon
T1_DAEMONS = 5
T1_MAX_COUNT = 1  # Numero de intentos del timer t1Daemon

#T2DAEMON
T2_DAEMONS = 5

#T3Daemon Solo hay 1 daemon tipo 3
T3_DAEMONS = 1

#Numero de buffers
BUFFERS = 5

# T1_TIMER_STATE = 3


class Daemons(Model):

    def init(self):
        self.t1_daemons = list()
        [self.t1_daemons.append(T1Daemon(daemon_id)) for daemon_id in range(T1_DAEMONS)]
        self.t2_daemons = list()
        [self.t2_daemons.append(T2Daemon(daemon_id)) for daemon_id in range(T2_DAEMONS)]
        self.t3_daemons = list()
        [self.t3_daemons.append(T3Daemon(daemon_id)) for daemon_id in range(T3_DAEMONS)]
        self.buffer = list()
        [self.buffer.append(buffer_id) for buffer_id in range(BUFFERS)]
        
        self.target_status = "ok"
        self.wait_status = False
        self.politica = "HIGH"
        self.status_daemons = [True, True, True]

        self.id_nodos = []  # Guarda el id del nodo que hizo la operacion de store de forma exitosa
        # QManager
        self.queue_high = [[] for __ in range(0)]  # skipcq
        self.queue_medium = [[] for __ in range(0)]  # skipcq
        self.queue_low = [[] for __ in range(0)]  # skipcq

        # Contador para politicas de servicio
        self.cont_prioridad_alta = 0  # skipcq
        # resultst1 existe
        self.cont_prioridad_media = 0  # skipcq
        self.cont_prioridad_baja = 0  # skipcq

        # Para T1
        self.T1 = [] * 3  # skipcq
        self.pendientes = []  # skipcq
        self.results_t1 = ""  # skipcq
        self.target = ""  # skipcq
        self.target_status = ""  # skipcq
        self.parametros_t1 = []  # skipcq
        self.operacion = ""  # skipcq
        self.espera = True  # skipcq
        self.result = "NONE"  # skipcq

    def receive(self, event):
        """ Funciona como interfsace, manda los mensajes a los elementos del sistema que corresponda. """

        if event.name == "DESPIERTA":
            Cliente(self)

        if event.target_element == "proxy":
            Proxy(self, event)

        if event.target_element == "buffer":
            buffer(self, event)

        if event.target_element == "qmanager":
            qManager(self, event)

        if event.target_element == "t1daemon":
            t1_Daemon(self, event)

        if event.target_element == "t2daemon":
            t2_Daemon(self,event)
        
        if event.target_element == "t3daemon":
            t3_Daemon(self, event)



# TODO: Hacer de los clientes una clase para poder simular varios
def Cliente(self):
    print("Que tipo de accion quieres realizar \n1)Store\n2)Retrieve\n")
    accion = 1  # Corresponde a store
    # Por ahora solo hace Store
    if accion == 1:
        # Ingresa archivo, lee nombre
        destino = random.randint(2, 4)  # ID del nodo
        # Los parametros vienen del cliente
        parametros = ["file", "name_file"]
        store(self, parametros, destino)
        print("Mando el Store al proxy " + str(destino))


def Proxy(self, event):
    print("##########################################################################################Proxy")
    '''ToDo: Generar nombre aleatorio '''
    if event.name == "STORE":
        """ Para referencia visual consultar Storage process, first phase (1) Client App Initiates """
        print("Soy el proxy de " + str(self.id) + " y hago uso de mi buffer ")
        file_, name_file = event.parametros
        new_name = generateNewName(name_file)
        print(new_name)
        parametros = [file_, new_name, NUM_COPIES]  # FileID es NewName
        store(self, parametros, self.id)

    'To ask: Proxy or elsewhere,como lo decidimos '


def buffer(self, event):
    print("########################################################################################## Buffer")
    if event.source_element == "proxy":  # '''To ask: or elseWhere , puede estar demas'''
        if event.name == "STORE":
            file_, new_name, num_copy = event.parametros  # File,FileName, nuCopy
            for copia in range(num_copy):  # Para cada copia
                id_nodo = invokeOracle()
                print("El id del nodo regresado por el Oraculo, es : " + str(id_nodo))
                # initiate(result = FAILURE_SUSPICION, reported=0)
                # reported = 0
                # NewName es unico para cada File
                parametros = {'file': file_, 'id_file': new_name,
                              'id_copy': copia, 'reported': 0}

                insert(self, "T1DaemonID", self.id, self.id, parametros,
                       "HIGH", "STORE", nodo_objetivo=id_nodo)
                # El insert es para su qmanager

    # TODO: QUIZA SE PUEDE GENERALIZAR REPORT PARA TODOS LOS TIPOS DE DEMONIOS
    if event.source_element == "t1daemon":
        if event.name == "REPORT":
            if event.operacion == "SUCESS" or event.parametros["reported"] >= MAX_FAILURES:
                print("La operacion fue un exito!!! o reportamos el fallo a proxy", event.name)
                confirmStorage(event.parametros["id_file"], event.parametros["id_copy"], event.name)
                update()  # TODO: Update, actualiza la lista del buffer segun IDFILE e idCopy
            else:  # Fue failure o reported < MAX_FAILURES (NO ESTOY SEGURO LOL)
                # if event.parametros["reported"] < MAX_FAILURES: Tomar en cuenta que si la operacion es FAILURE
                # en event.operacion viene la opericon que se intento en el nodo, no "FAILURE", si fue SUCESS en
                # operacion se pone SUCESS en lugar de la operacion que se intento
                print("La operacion fallo, lo intentamos de nuevo")
                insert(self, "T1DaemonId", self.id, self.id, event.parametros, event.prioridad,
                       event.operacion, event.nodo_objetivo)

        if event.name == "STORE":
            # Viene de invokeTask de T1Daemon, le pide hacer esta operacion porque fue elegido por el oraculo.
            print("tengo que hacer un store! Mando mensaje de confirmacion a t1 daemon, o no", event.source_element_id)
            if event.parametros["id_copy"] > 1:
                # Creo clones
                print("Funiona!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!?")
                insert(self, "T3DaemonID", self.id, self.id, event.parametros, "HIGH", "STORE",
                       buffer_id=self.buffer[0], timer=10, source_daemon=event.source_element_id
                       ,tipo_daemon= "T1DaemonID")
                       #TODO:Eliminar numero magico: Timer, mejorar seleccion de buffers
            else:
                print("Vamos a mandar confirStorage, soy el original",event.parametros["id_copy"])

            resultados = True  # ! Variable de prueba, esto lo deberia de regresar un proceso
            if resultados:
                report(self, resultados)


def qManager(self, event):  # QManager
    print("########################################################################################## QManager")
    # Cualquier cosa que le llega, la encola segun su prioridad
    print("Evento:", event.name)
    print("Operacion", event.operacion)
    
    if event.name == "T1DaemonID":
        if event.operacion == "STORE":
            # Ver diagrada Sotage process, first phase, le sigue Queue Manager & type 1
            # execution daemon with delayed answer
            print("Para el t1 DAEMON")
            print("La prioridad es :", event.prioridad)
            elementos = [1, event.target, event.source, event.operacion, event.parametros]
            encolar(self, elementos, event.prioridad)
            print("Deberia encolar!!!!!")

        if event.operacion == "RETRIEVE":
            print("Ver diagrama Retrieeval process, first phase")

        if event.operacion == "PROCESS":
            print("Ver diagrama Storage process, last phase/second phase")
        if event.operacion == "ELIMINATECOPY":
            print("Ver diagrama Storage process, second phase")

    if event.name == "T2DaemonID":
        if event.operacion == "STORE":  # Quiza esta demas ?
            print("Ver diagrama Storage process, second phase")

    if event.name == "T3DaemonID":
        if event.operacion == "STORE":
            print("Para el t3 Daemon")
            elementos = [3, event.target, event.source, event.operacion, event.parametros]
            encolar(self, elementos, event.prioridad)
            print("Debe encolar")

        # ! ESTO DEBERIA DE ESTAR POR SEPARADO, PARA QUE ESTE EN CONTINUA EJECUCION SIN IMPORTAR LOS MENSAJES QUE LE
        # LLEGUEN
        '''
        Politica de Servicio:
            Por cada 3 tareas de alta prioridad se despacha 1 de prioridad Media y
            por cada 2 tareas de priorida media se despacha 1 de prioridad Baja
        '''
    daemon_do(self)

    if event.name == "FREE":
        # TODO: A MENOS QUE TODOS ESTEN LIBRES DE NUEVO SE USA EL METODO daemon_do, de otra forma se le asigna el
        #  que puedea hacer
        print("Se libero el daemon tipo", event.operacion, "Con Id:", event.target_element_id)
        daemon_type = int(event.operacion) - 1
        if not self.status_daemons[daemon_type]:
            print("Ya hay demonios tipo", event.operacion, "disponibles")
            self.status_daemons[daemon_type] = True

            # TODO: Todos los demonios estan ocupados, entonces nada de lo de arriba se ejecuta, agregar un entra para
            #  cuando llegue el mensaje del demonio cuando se desocupa


# T1Deamon no se activa con mensajes para forzar que se tega que esperar su ejecucion
# Con la finalidad de cumplir con la condicion de que tiene que confirmar la conclusion de su tarea
def t1_Daemon(self, event):
    print("########################################################################################## DEMON 1")
    # Ver: Que Manager & Type 1 Execution Daemon, with delayed answer
    if event.name == "EXECUTE":
        print("Mando execute desde t1Daemon method", event.target_element_id)
        self.t1_daemons[event.target_element_id].execute(self, event)

    if event.name == "TIMER":
        print("Recibo timer desde t1Daemon method", event.target_element_id)
        self.t1_daemons[event.target_element_id].timer(self)

    if event.name == "CONFIRM":
        pass


def t2_Daemon(self, event):
    print("########################################################################################## DEMON 3")
    if event.name == "no me acuerdo we ":
        pass


def t3_Daemon(self, event):
    print("########################################################################################## DEMON 3")
    if event.name == "EXECUTE":
        print("ESTE ES EL DEMONIO TIPO 3")
        self.t3_daemons[event.target_element_id].execute(self, event)
    if event.name == "TIMER":
        # El parametro event.nodo_objetivo contiene el clone_id
        self.t3_daemons[event.target_element_id].timer(self, event.nodo_objetivo)
        


def invokeOracle():
    print("Oracle invocado")
    # ! Numeros magicos!!!!!
    # TODO:Segun topo.txt del nodo 5 al 8 son nodos encargados de almacenar
    return random.randint(5, 8)


# skipcq: PYL-W0613
def generateNewName(name_file):
    return id(name_file)


def waitResult(self):
    pass


# skipcq: PYL-W0613
def report(self, results):
    print("Reporto los resultados ")

    pass
    # print("                 El resultado de la operacion fue: " + str(self.result))


# skipcq: PYL-W0613
def update():
    print("Hago update")
    pass


def confirmStorage(id_file, id_copy, result):
    # TODO: DEBE DE TENER UN CONTADOR PARA CADA IDFILE DISTINTO, CUANDO LLEGUE RESULTADOS\
    #   LOS ANOTA EN UN CONTADOR, CUANDO EL CONTADOR ESTE  LISTO, CONFIRMA A CLIENTAPP 
    print("Confirmo que ya esta guardado")
    pass


# ----------------------------------------------------------------------------------------
# "main()"
# ----------------------------------------------------------------------------------------

# construye una instancia de la clase Simulation recibiendo como parametros el nombre del
# archivo que codifica la lista de adyacencias de la grafica y el tiempo max. de simulacion
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Please supply a file name")
        raise SystemExit(1)
    experiment = Simulation(sys.argv[1], 500)

    # asocia un pareja proceso/modelo con cada nodo de la grafica
    for i in range(1, len(experiment.graph) + 1):
        m = Daemons()
        experiment.setModel(m, i)

    # inserta un evento semilla en la agenda y arranca

    seed = Mensaje("DESPIERTA", "", 0.0, 1, 1, None,
                   None, None, None, None, None, 0)

    experiment.init(seed)

    experiment.run()



def prueba():
    lista = [1,2,3,4,'funciona']
    print(lista)
    return lista