"""
Junta todas las constantes del sistema y los metodos que involucran la salida al GUI
Esta por separado para evitar importes circulares.
"""


class Globals:
    """Proporciona la variable global que se utilizara para mandar al contexto de la GUI
    y la manipulacion de la variable se definen mas abajo"""
    resultado_ids = [
        [['Copy 0'], ['all']],
        [['Copy 1'], ['all']],
        [['Copy 2'], ['all']]
    ]


def add_result(self, id_copy, contenido, color="all"):
    Globals.resultado_ids[id_copy][0].append(f'[{self.clock}|{self.id}]: {contenido}')
    Globals.resultado_ids[id_copy][1].append(color)
    # print(f'[{self.clock}]: {contenido}')


def add_all(self, contenido, color="all"):
    for elemento in range(len(Globals.resultado_ids)):
        Globals.resultado_ids[elemento][0].append(
            f'[{self.clock}|{self.id}]:[ALL]: {contenido}'
        )
        Globals.resultado_ids[elemento][1].append(color)
    # print(f'[{self.clock}]: {contenido}')


#
def clear():
    Globals.resultado_ids = [
        [['Copy 0'], ['all']],
        [['Copy 1'], ['all']],
        [['Copy 2'], ['all']]
    ]

    return Globals.resultado_ids


def regresa():
    return Globals.resultado_ids


class Config:
    """Constantes necesarias para el algoritmo, si se quiere modificar el comportamiento
        aqui se modifican la constantes necesarias. 
    """
    # Tiempo en el que se mandan los mensajes: self.clock+TIME
    TIME = 1

    # Numero de intentos de insert si el resultado de este fue FAILURE_SUSPICION
    MAX_FAILURES = 1

    # Numero de copias creadas por archivo
    NUM_COPIES = 3

    # Politicas de servicio Qmanager
    PRIORIDAD_ALTA = 3
    EJECUTA_PRIORIDAD_ALTA = 3
    EJECUTA_PRIORIDAD_MEDIA = 1
    PRIORIDAD_MEDIA = 3
    EJECUTA_PRIORIDAD_BAJA = 1
    PRIORIDAD_BAJA = 1

    T1_DAEMONS = 5  # Numero de dameons tipo 1
    T1_MAX_COUNT = 1  # Numero de intentos del timer t1Daemon

    T2_DAEMONS = 5  # Numero de daemon tipo 2

    # T3Daemon Solo hay 1 daemon tipo 3
    T3_DAEMONS = 1

    # Numero de buffers
    BUFFERS = 5

    # Numero de intentos en T1Daemon, en diagramas se llama MAXCOUNT
    T1_TIMER_STATE = 3

    # Cuantas copias son necesarias que se almacenen para poder confirmar al cliente
    CONFIRM_COPIES = 1

    # Define el rol de los nodos, dado por su id
    NODO_CLIENTE = 1
    # Si los nodos que son proxies son: 2,3,4
    NODO_PROXY_LOWER = 2
    NODO_PROXY_UPPER = 4
    # Si los nodos que son servers son: 5,6,7,8
    NODO_SERVER_LOWER = 5
    NODO_SERVER_UPPER = 8

    # Timer para t3Daemon
    CLONE_TIMER = 1



    #Tamano de la UMA
    UMA = 5
