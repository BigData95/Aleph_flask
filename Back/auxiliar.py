import re

import random
from .mensajes import *
from .salidas import add_result, add_all

"""
Metodos necesarios para el algoritmo, pero que no aparecen en los diagramas o
que se dedican a hacer otra clase de operaciones no relacionadas directamente con 

"""
PRIORIDAD_ALTA = 3
PRIORIDAD_MEDIA = 3
PRIORIDAD_BAJA = 3


def encargoDaemon(self, nodo_info, prioridad, id_daemon, id_copy):
    # next_task = []
    if prioridad == "HIGH":
        next_task = self.queue_high.pop(0)
        self.cont_prioridad_alta += 1
    elif prioridad == "MEDIUM":
        next_task = self.queue_medium.pop(0)
        self.cont_prioridad_media += 1  # if self.cont_prioridad_media < PRIORIDAD_MEDIA else 0
    elif prioridad == "LOW":
        next_task = self.queue_low.pop(0)
        self.cont_proridad_baja += 1
    else:
        raise ValueError("La prioridad no se encuentra definida")

    # print("MANDO EXECUTE AL", id_daemon, "PRIORIDAD:", prioridad)
    add_result(nodo_info, id_copy, f'Mando execute al {id_daemon} Prioridad: {prioridad}', "qmanager")
    # _, target_nodo, source, operacion, parametros = next_task.values()
    execute(nodo_info,
            next_task['nodo_objetivo'],
            next_task['source'],
            next_task['operacion'],
            next_task['parametros'],
            prioridad,
            id_daemon,
            next_task['tipo_daemon']
            )


def getIndexPositions(list_elements, element):
    """ Returns the indexes of all occurrences of give element in
    the list- listOfElements """
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


def check_daemons(self, nodo_info, daemon_type):
    if daemon_type == 1 and freeDaemon(nodo_info.t1_daemons) == -1:
        self.status_daemons[0] = False
    if daemon_type == 2 and freeDaemon(nodo_info.t2_daemons) == -1:
        self.status_daemons[1] = False
    # if daemon_type == 3 and freeDaemon(self.t3_daemons) == -1:
    #     self.status_daemons[2] = False


def freeDaemon(daemons_list):
    for daemon in range(len(daemons_list)):
        if daemons_list[daemon].status == "FREE":
            return daemons_list[daemon].daemon_id
    return -1


def encolar(self, elementos, prioridad):
    if prioridad == "HIGH":
        # print("Estoy encolado: SOY PRIORIDAD ALTA")
        self.queue_high.append(elementos)
    if prioridad == "MEDIUM":
        # print("Estoy encolado: SOY PRIORIDAD MEDIA")
        self.queue_medium.append(elementos)
    if prioridad == "LOW":
        # print("Estoy encolado: SOY PRIORIDAD BAJA")
        self.queue_low.append(elementos)


# import time

# def daemon_do(self, id_copy=None):
#     if True in self.status_daemons:
#         # print("HAY DEMONIOS")
#         despachado = False
#         while (self.queue_high or self.queue_medium or self.queue_low) and not despachado:
#             free_daemons = getIndexPositions(self.status_daemons, True)
#             if self.politica == "HIGH":
#                 if self.queue_high:
#                     prueba2(self, self.queue_high, free_daemons, "HIGH", id_copy)
#                     despachado = True
#                 else:  # NO HAY NADA EN LA LISTA DE PRIORIDAD ALTA, CAMBIAMOS POLITICA
#                     print("@@No hay nada en la lista de prioirdad alta, cambiamos politica, vamos media")
#                     self.politica = "MEDIUM"
#             if self.politica == "MEDIUM":
#                 print("Entro aca")
#                 if self.queue_medium:
#                     prueba2(self, self.queue_medium, free_daemons, "MEDIUM", id_copy)
#                     despachado = True
#                 else:
#                     print("@@No hay nada en la lista de prioirdad media, cambiamos politica, vamos baja")
#                     self.politica = "LOW"
#             if self.politica == "LOW":
#                 if self.queue_low:
#                     prueba2(self, self.queue_low, free_daemons, "LOW", id_copy)
#                     despachado = True
#                 else:
#                     print("@@No hay nada en la lista de prioirdad baja, cambiamos politica,vamos alta")
#                     self.politica = "HIGH"
#         else:
#             print("No hay tareas pendientes", self.politica)
#             print(self.queue_high)
#     else:
#         print("No hay demonios disponibles")


# def prueba2(self, queue, free_daemons, prioridad, id_copy):
#     for _ in range(len(queue)):
#         tipo_daemon = queue[0]['tipo_daemon']
#         if tipo_daemon == 1 and 1 in free_daemons:
#             get_free_daemon = freeDaemon(self.t1_daemons)
#             if get_free_daemon != -1:
#                 print("Se envia trabajo al T1Daemon:", get_free_daemon)
#                 add_result(self, id_copy, f'Se envia trabajo al T1Daemon: {get_free_daemon}', "qmanager")
#                 encargoDaemon(self, prioridad, get_free_daemon, id_copy)
#                 self.t1_daemons[get_free_daemon].status = "BUSY"  # Para evitar errores
#                 # Revisa si hay mas libres aparte de el, cambia a false si no hay
#                 check_daemons(self, 1)
#             else:  # No hay demonios disponibles
#                 self.status_daemons[0] = False
#                 print(free_daemons)
#                 add_result(self, id_copy, f'{free_daemons}', "qmanager")
#                 print("Ya no hay demonios T1Daemons")
#                 add_result(self, id_copy, "Ya no hay T1Daemons", "qmanager")
#                 break
#         elif tipo_daemon == 2 and 2 in free_daemons:
#             get_free_daemon = freeDaemon(self.t2_daemons)
#             if get_free_daemon != -1:
#                 print("Se envia trabajo al T2Daemon:", get_free_daemon)
#                 add_result(self, id_copy, f'Se envia trabajo al T2Daemon: {get_free_daemon}', "qmanager")
#                 encargoDaemon(self, prioridad, get_free_daemon, id_copy)
#                 self.t2_daemons[get_free_daemon].status = "BUSY"
#                 check_daemons(self, 2)
#             else:
#                 self.status_daemons[1] = False
#                 print("Ya no hay demonios T2Daemons")
#                 add_result(self, id_copy, "Ya no hay T2Daemons", "qmanager")
#         elif tipo_daemon == 3 and 3:  # in free_daemons:
#             # El demonio tipo 3 siempre esta disponible
#             # todo: Solo deberia de hacer referencia a un demonio tipo 3
#             get_free_daemon = freeDaemon(self.t3_daemons)  # SOlo hay un demonio tipo 3
#             print("Se envia trabajo al T3Daemon:", get_free_daemon)
#             add_result(self, id_copy, f'Se envia trabajo al T3Daemon: {get_free_daemon}', "qmanager")
#             encargoDaemon(self, prioridad, get_free_daemon, id_copy)
#             # if get_free_daemon != -1:
#             #     print("Daemon tipo 3 se le envio el trabajo:", get_free_daemon)
#             #     encargoDaemon(self, prioridad, get_free_daemon, tipo_daemon)
#             #     self.t3_daemons[get_free_daemon].status = "BUSY"
#             #     check_daemons(self, 3)
#             # else:
#             #     self.status_daemons[2] = False
#             #     print("Ya no hay demonios tipo 3")
#         # else:
#         #     print("Algo malo paso, ver linea 143")
#         #     break
#         contPrioridad(self, prioridad)


def contPrioridad(self, prioridad):
    if prioridad == "HIGH" and self.cont_prioridad_alta > PRIORIDAD_ALTA:
        self.cont_prioridad_alta = 0
        # print("CAMBIO!!! a medium por politica")
        self.politica = "MEDIUM"
    elif prioridad == "MEDIUM" and self.cont_prioridad_media > PRIORIDAD_MEDIA:
        self.cont_prioridad_media = 0
        self.poltica = "LOW"
    elif prioridad == "LOW" and self.cont_proridad_baja > PRIORIDAD_BAJA:
        self.cont_proridad_baja = 0
        self.politica = "HIGH"


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


def update():
    print("Hago update")


def generateNewName(file_name):
    return id(file_name)


def confirmStorage2(self, id_file, id_copy, result):
    # TODO: DEBE DE TENER UN CONTADOR PARA CADA IDFILE DISTINTO, CUANDO LLEGUE RESULTADOS\
    #   LOS ANOTA EN UN CONTADOR, CUANDO EL CONTADOR ESTE  LISTO, CONFIRMA A CLIENTAPP
    print("Confirmo que ya esta guardado")
    add_result(self, id_copy, "Confirmo que ya esta guardado", "buffer")
    pass


def invokeOracle():
    # print("Oracle invocado")
    # ! Numeros magicos!!!!!
    # TODO:Segun topo.txt del nodo 5 al 8 son nodos encargados de almacenar
    return random.randint(5, 8)
