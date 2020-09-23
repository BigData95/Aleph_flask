import re
from typing import List

import random

from back.aleph.daemons.daemons import Daemon
from .mensajes import *
from .salidas import add_result
from .config import Config
from back.simulador import Simulation

"""
Metodos necesarios para el algoritmo, pero que no aparecen en los diagramas o
que se dedican a hacer otra clase de operaciones que se pueden generalizar.
"""


def encargoDaemon(self, nodo_info, prioridad, id_daemon, id_copy):
    """Auxiliar: Se encarga de mandar activar daemon, con la operacion correspondiente"""
    if prioridad == "HIGH":
        next_task = self.queue_high.pop(0)
        self.cont_prioridad_alta += 1
    elif prioridad == "MEDIUM":
        next_task = self.queue_medium.pop(0)
        self.cont_prioridad_media += 1
    elif prioridad == "LOW":
        next_task = self.queue_low.pop(0)
        self.cont_proridad_baja += 1
    else:
        raise ValueError("La prioridad no se encuentra definida")

    add_result(nodo_info, id_copy, f'Mando execute al {id_daemon} Prioridad: {prioridad}', "qmanager")
    execute(nodo_info,
            next_task['nodo_objetivo'],
            next_task['source'],
            next_task['operacion'],
            next_task['parametros'],
            prioridad,
            id_daemon,
            next_task['tipo_daemon'],
            next_task['id_daemon_objetivo']
            )


def getIndexPositions(list_elements, element) -> List[int]:
    """Auxiliar:Regresa los indexes de todas las ocurrencias en la lista \
    de algun elemento dado"""
    indexPosList = []
    indexPos = 0
    while True:
        try:
            # Search for item in list from indexPos to the end of list
            indexPos = list_elements.index(element, indexPos)
            # Add the index position in list
            indexPosList.append(indexPos + 1)
            indexPos += 1
        except ValueError as e:
            break
    return indexPosList


def check_daemons(self, nodo_info, daemon_type: int) -> None:
    """ Auxiliar: Revisa si hay algun daemon libre del tipo de deamon particular que le pasan\
        como parametro. Avisa que no hay demonios disponibles de ese tipo.
    """
    if daemon_type == 1 and freeDaemon(nodo_info.t1_daemons) == -1:
        self.status_daemons[0] = False
    if daemon_type == 2 and freeDaemon(nodo_info.t2_daemons) == -1:
        self.status_daemons[1] = False
    # if daemon_type == 3 and freeDaemon(self.t3_daemons) == -1:
    #     self.status_daemons[2] = False


def freeDaemon(daemons_list: List[Daemon]) -> int:
    """ Auxiliar: Busca en la lista de daemons (Apelh()) si hay algun daemon \
     con estado "FREE", y si lo hay regresa su index. De lo contrario regresa un \
     valor falsy
     """
    for daemon in range(len(daemons_list)):
        if daemons_list[daemon].status == "FREE":
            return daemons_list[daemon].daemon_id
    return -1


def encolar(self, elementos, prioridad):
    """Auxiliar: Agrega a la cola segun corresponda"""
    if prioridad == "HIGH":
        self.queue_high.append(elementos)
    if prioridad == "MEDIUM":
        self.queue_medium.append(elementos)
    if prioridad == "LOW":
        self.queue_low.append(elementos)


def contPrioridad(self, prioridad):
    if prioridad == "HIGH" and self.cont_prioridad_alta > Config.PRIORIDAD_ALTA:
        self.cont_prioridad_alta = 0
        self.politica = "MEDIUM"
    elif prioridad == "MEDIUM" and self.cont_prioridad_media > Config.PRIORIDAD_MEDIA:
        self.cont_prioridad_media = 0
        self.poltica = "LOW"
    elif prioridad == "LOW" and self.cont_proridad_baja > Config.PRIORIDAD_BAJA:
        self.cont_proridad_baja = 0
        self.politica = "HIGH"


# ! Warning: No deberia de regresar distintos tipos
def toList(lista, tipo):
    """Auxiliar: Convierte un String a una lista de enteros, \
    funciona si el string esta delimitado por: , - o un espacio  """
    respuesta = list()
    "Si se agregan delimitadores, cambiar la expresion regular en forms.py"
    delimitadores = " ", ",", "-"
    regex = '|'.join(map(re.escape, delimitadores))
    prelista = re.split(regex, lista)
    # prelista = lista.split(',')
    # nuevo = ""
    for elemento in prelista:
        if tipo == "float":
            nuevo = float(elemento)
        elif tipo == "int":
            nuevo = int(elemento)
        respuesta.append(nuevo)
    return respuesta


def generateNewName(file_name: str) -> id:
    """Auxiliar: Genera un id unico para el file"""
    return id(file_name)


def invokeOracle() -> int:
    """Auxiliar: Regresa un numero aleatorio entre 5 y 8"""
    # ! Numeros magicos!!!!!
    # TODO:Segun topo.txt del nodo 5 al 8 son nodos encargados de almacenar
    return random.randint(Config.NODO_SERVER_LOWER, Config.NODO_SERVER_UPPER)


def seed_all(experiment: Simulation, numero_nodos: int, mensaje: str,
             lista_fallo: list, tiempo_fallo: list, tiempo_recuperacion: list):
    """
    Auxiliar: Genera semillas. En este caso manda a los nodos que van a fallar la informacion que necesitan para
    simular el fallo y la recuperacion. Si se quita el if, se puede ver como una especie de broadcast
    """
    for nodo in range(1, numero_nodos + 1):
        if nodo in lista_fallo:
            seed = Mensaje(mensaje, 0.0, nodo, nodo,
                           lista_fallo=lista_fallo,
                           tiempo_fallo=tiempo_fallo,
                           tiempo_recuperacion=tiempo_recuperacion)
            experiment.init(seed)
