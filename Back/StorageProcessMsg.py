import copy
import random
# import sys
import pathlib

#todo: Hacer solo los import necesarios
from .auxiliar import daemon_do, encolar
from .daemons import T1Daemon, T2Daemon, T3Daemon
from .salidas import add_all, add_result, regresa  
from .mensajes import *
# Del simulador
from .simulador import Model, Simulation




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


T1_DAEMONS = 5    # Numero de dameons tipo 1 
T1_MAX_COUNT = 1  # Numero de intentos del timer t1Daemon

T2_DAEMONS = 5    # Numero de daemon tipo 2

#T3Daemon Solo hay 1 daemon tipo 3
T3_DAEMONS = 1

#Numero de buffers
BUFFERS = 5





class Aleph(Model):

    def __init__(self):
        super().__init__()
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
        self.queue_high = [[] for __ in range(0)] 
        self.queue_medium = [[] for __ in range(0)]
        self.queue_low = [[] for __ in range(0)]  

        # Contador para politicas de servicio
        self.cont_prioridad_alta = 0 
        self.cont_prioridad_media = 0
        self.cont_prioridad_baja = 0  



    def receive(self, event):
        """ Funciona como interfaz, manda los mensajes a los elementos del sistema que corresponda. """

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
    """

    """
    print("Que tipo de accion quieres realizar \n1)Store\n2)Retrieve\n")
    accion = 1 
    # Por ahora solo hace Store
    if accion == 1:
        # Ingresa archivo, lee nombre
        destino = random.randint(2, 4)  # ID del nodo
        
        # Los parametros vienen del cliente
        parametros = ["file", "file_name"]
        
        store(self, parametros, destino)
        print(f'Mando Store al Proxy:{destino}')
        add_all(self, f'Mando Store al Proxy:{destino}')


def Proxy(self, event):
    print("##Proxy##")
    add_all(self, "##Proxy")
    if event.name == "STORE":
        """ Para referencia visual consultar Storage process, first phase (1) Client App Initiates """
        print(f'Proxy de: {self.id}, uso buffer')
        add_all(self, f'Proxy de: {self.id}, uso buffer')
        file_, file_name = event.parametros
        new_name = generateNewName(file_name)
        # print(new_name)
        parametros = [file_, new_name, NUM_COPIES]  # FileID es NewName
        store(self, parametros, self.id) # Para buffer

    'To ask: Proxy or elsewhere,como lo decidimos '


def buffer(self, event):
    print("##Buffer##")
    if event.source_element == "proxy": 
        if event.name == "STORE":
            file_, new_name, num_copy = event.parametros  # File,FileName, nuCopy
            for copia in range(num_copy):  # Para cada copia
                # add_result(self, copia, "Oracle Invocado")
                id_nodo = invokeOracle()
                add_result(self, copia, "##Buffer##")
                add_result(self, copia,
                        f"Id del nodo regresado por oraculo: {id_nodo}")
                print("El id del nodo regresado por el Oraculo, es : " + str(id_nodo))
                # initiate(result = FAILURE_SUSPICION, reported=0)
                # reported = 0
                # NewName es unico para cada File
                parametros = {
                            'file': file_, 
                            'id_file': new_name,
                            'id_copy': copia, 
                            'reported': 0
                            }
                insert(self,  #Para qManager
                    "T1DaemonID",
                    self.id,    
                    self.id, 
                    parametros,
                    "HIGH", 
                    "STORE", 
                    nodo_objetivo=id_nodo
                    )

    # TODO: QUIZA SE PUEDE GENERALIZAR REPORT PARA TODOS LOS TIPOS DE DEMONIOS
    if event.source_element == "t1daemon":
        if event.name == "REPORT":
            add_result(self, event.parametros['id_copy'], "##Buffer##")
            if event.operacion == "SUCESS" or event.parametros["reported"] >= MAX_FAILURES:
                add_result(self, event.parametros["id_copy"] , f"Operacion exito {event.name}")
                print(f"Operacion exito {event.name}")
                confirmStorage(event.parametros["id_file"], event.parametros["id_copy"], event.name)
                update()  # TODO: Update, actualiza la lista del buffer segun IDFILE e idCopy
            else:  # Fue failure o reported < MAX_FAILURES (NO ESTOY SEGURO LOL)
                # if event.parametros["reported"] < MAX_FAILURES: Tomar en cuenta que si la operacion es FAILURE
                # en event.operacion viene la opericon que se intento en el nodo, no "FAILURE", si fue SUCESS en
                # operacion se pone SUCESS en lugar de la operacion que se intento

                # add_result(self, 'all', f"{event.parametros}")
                add_result(self, event.parametros['id_copy'] , "La operacion fallo, lo intentamos de nuevo")
                print("La operacion fallo, lo intentamos de nuevo")
                insert(self,
                        "T1DaemonId",
                        self.id,
                        self.id,
                        event.parametros,
                        event.prioridad,
                        event.operacion, 
                        event.nodo_objetivo
                        )

        if event.name == "STORE":
            # Viene de invokeTask de T1Daemon, le pide hacer esta operacion porque fue elegido por el oraculo.
            print("tengo que hacer un store! Mando mensaje de confirmacion a t1 daemon, o no", event.source_element_id)
            add_result(self, event.parametros['id_copy'], '##Buffer##')
            add_result(self, event.parametros['id_copy'],
                        f'Tengo que hacer un Store. Mando ensaje de confirmacion a t1Daemon {event.source_element_id}')
            if event.parametros["id_copy"] > 1:
                # Creo clones
                print("Funiona!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!?")
                insert(self, 
                    "T3DaemonID", 
                    self.id, 
                    self.id, 
                    event.parametros, 
                    "HIGH", 
                    "STORE",
                    buffer_id=self.buffer[0], 
                    timer=10, 
                    source_daemon=event.source_element_id,
                    tipo_daemon="T1DaemonID"
                    )
            else:
                print("Vamos a mandar confirStorage, soy el original",event.parametros["id_copy"])
                add_result(self, event.parametros['id_copy'], 
                            'Vamos a mandar confirmStorage, soy el original' )

            resultados = True  # ! Variable de prueba, esto lo deberia de regresar un proceso
            if resultados:
                print(f'Parametos en resulados {event.parametros}')
                add_all(self, f'Parametros en resultados {event.parametros}')
                report(self, resultados)


def qManager(self, event):  # QManager
    # Este if esta pensando en la salida de GUI. 
    # if event.parametros != None:
    #     add_result(self, event.parametros['id_copy'] , "##Proxy##")
    print("########################################################################################## QManager")

    # Cualquier cosa que le llega, la encola segun su prioridad
    print("Evento:", event.name)
    print("Operacion", event.operacion)
    
    if event.name == "T1DaemonID":
        #!HOTFIX
        add_result(self, event.parametros['id_copy'], "#QManager#")
        if event.operacion == "STORE":
            # Ver diagrada Sotage process, first phase, le sigue Queue Manager & type 1
            # execution daemon with delayed answer
            
            print("Para el t1 DAEMON")
            add_result(self, event.parametros['id_copy'], "Para el T1Daemon")
            add_result(self, event.parametros['id_copy'], f'La prioridad es: {event.prioridad}')
            print("La prioridad es :", event.prioridad)

            # elementos = [1, event.nodo_objetivo, event.source, event.operacion, event.parametros]
            elementos = {
                'tipo_daemon': 1,
                'nodo_objetivo': event.nodo_objetivo,
                'source': event.source,
                'operacion': event.operacion,
                'parametros': event.parametros
            }
            encolar(self, elementos, event.prioridad)
            print("Deberia encolar!!!!!")
            add_result(self, event.parametros['id_copy'], "Deberia encolar")

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
            add_result(self, event.parametros['id_copy'] , "Para el T3Daemon")
            print("Para el t3 Daemon")
            # elementos = [3, event.target, event.source, event.operacion, event.parametros]
            elementos = {
                'tipo_daemon': 3,
                'nodo_objetivo': event.target,
                'source': event.source,
                'operacion': event.operacion,
                'parametros': event.parametros
            }
            encolar(self, elementos, event.prioridad)
            print("Debe encolar")
            add_result(self, event.parametros['id_copy'] , "Debe encolar")

        # ! ESTO DEBERIA DE ESTAR POR SEPARADO, PARA QUE ESTE EN CONTINUA EJECUCION SIN IMPORTAR LOS MENSAJES QUE LE
        # LLEGUEN
        '''
        Politica de Servicio:
            Por cada 3 tareas de alta prioridad se despacha 1 de prioridad Media y
            por cada 2 tareas de priorida media se despacha 1 de prioridad Baja
        '''
    if event.parametros != None:
        daemon_do(self, event.parametros['id_copy'])
    else:
        daemon_do(self)

    if event.name == "FREE":
        # TODO: A MENOS QUE TODOS ESTEN LIBRES DE NUEVO SE USA EL METODO daemon_do, de otra forma se le asigna el
        add_all(self, '##QManager##')
        #  que puedea hacer
        add_all(self, f'Se libero el daemon tipo {event.operacion}. ID:{event.target_element_id}')
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
    print(f'Estos son los parametros:{event.parametros}')
    add_result(self, event.parametros['id_copy'], "##T1Daemon##")
    # Ver: Que Manager & Type 1 Execution Daemon, with delayed answer
    if event.name == "EXECUTE":
        add_result(self, event.parametros['id_copy'] ,
                    f'Execute desde T1Daemon {event.target_element_id}')
        print("Mando execute desde t1Daemon method", event.target_element_id)
        self.t1_daemons[event.target_element_id].execute(self, event)

    if event.name == "TIMER":
        print("Timer desde T1Daemon", event.target_element_id)
        add_result(self, event.parametros['id_copy'] , 
                   f'Timer desde T1Daemon {event.target_element_id}')
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
        add_result(self, event.parametros['id_copy'] , "Este es el T3Daemon: Execute")
        print(event.parametros)
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


def confirmStorage(id_file, id_copy, result):
    # TODO: DEBE DE TENER UN CONTADOR PARA CADA IDFILE DISTINTO, CUANDO LLEGUE RESULTADOS\
    #   LOS ANOTA EN UN CONTADOR, CUANDO EL CONTADOR ESTE  LISTO, CONFIRMA A CLIENTAPP 
    print("Confirmo que ya esta guardado")
    pass


    
# resultado_ids = [['Copy 1'], ['Copy 2'], ['Copy 3']]

# def add_result(self, id, contenido):
#     global resultado_ids
#     resultado_ids[id].append(f'[{self.clock}]: {contenido}')
#     # print(f'[{self.clock}]: {contenido}')


# def add_all(self, contenido):
#     global resultado_ids
#     for elemento in range(len(resultado_ids)):
#         resultado_ids[elemento].append(
#             f'[{self.clock}]:[ALL]: {contenido}'
#         )
#     # print(f'[{self.clock}]: {contenido}')



# ----------------------------------------------------------------------------------------
# "main()"
# ----------------------------------------------------------------------------------------



def inicia(lista_fallo=None, tiempo_fallo=None, tiempo_recuperacion=None):
    # import pathlib
    fn = pathlib.Path(__file__).parent / 'topo.txt'
    
    experiment = Simulation(fn, 500)

    # asocia un pareja proceso/modelo con cada nodo de la grafica
    for i in range(1, len(experiment.graph) + 1):
        m = Aleph()
        experiment.setModel(m, i)

    # inserta un evento semilla en la agenda y arranca
    seed = Mensaje(
            "DESPIERTA", # Name
            "",          # operacion
            0.0,         # Time
            1,           # Target
            1,           # Source
            None,        # elemento_interno_objetivo
            None,        # elemento_interno_remitente 
            None,        # elem_int_obj_id
            None,        # elem_int_rem_id 
            None,        # parametros 
            None,        # prioridad
            None,        # nodo_objetivo
            lista_fallo,        # lista_fallo
            tiempo_fallo,        # tiempo_fallo
            tiempo_recuperacion,        # tiempo_recuperacion
            0            # Port=0
                )

    experiment.init(seed)
    experiment.run()

    return regresa()
