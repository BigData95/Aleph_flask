from .mensajes import *

"""
Metodos necesarios para el algoritmo, pero que no aparecen en los diagramas
"""
PRIORIDAD_ALTA = 3
PRIORIDAD_MEDIA = 3
PRIORIDAD_BAJA = 3


def encargoDaemon(self, prioridad, id_daemon, tipo_daemon):
    next_task = []
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

    print("MANDO EXECUTE AL", id_daemon, "PRIORIDAD:", prioridad)
    _, target_nodo, source, operacion, copy = next_task
    execute(self, target_nodo, source, operacion, copy, prioridad, id_daemon, tipo_daemon)


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


def check_daemons(self, daemon_type):
    if daemon_type == 1 and freeDaemon(self.t1_daemons) == -1:
        self.status_daemons[0] = False
    if daemon_type == 2 and freeDaemon(self.t2_daemons) == -1:
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
        print("Estoy encolado: SOY PRIORIDAD ALTA")
        self.queue_high.append(elementos)
    if prioridad == "MEDIUM":
        print("Estoy encolado: SOY PRIORIDAD MEDIA")
        self.queue_medium.append(elementos)
    if prioridad == "LOW":
        print("Estoy encolado: SOY PRIORIDAD BAJA")
        self.queue_low.append(elementos)


import time


def daemon_do(self):
    if True in self.status_daemons:
        # print("HAY DEMONIOS")
        despachado = False
        while (self.queue_high or self.queue_medium or self.queue_low) and not despachado:
            free_daemons = getIndexPositions(self.status_daemons, True)
            if self.politica == "HIGH":
                if self.queue_high:
                    prueba2(self, self.queue_high, free_daemons, "HIGH")
                    despachado = True
                else:  # NO HAY NADA EN LA LISTA DE PRIORIDAD ALTA, CAMBIAMOS POLITICA
                    print("@@No hay nada en la lista de prioirdad alta, cambiamos politica, vamos media")
                    self.politica = "MEDIUM"
            if self.politica == "MEDIUM":
                print("Entro aca")
                if self.queue_medium:
                    prueba2(self, self.queue_medium, free_daemons, "MEDIUM")
                    despachado = True
                else:
                    print("@@No hay nada en la lista de prioirdad media, cambiamos politica, vamos baja")
                    self.politica = "LOW"
            if self.politica == "LOW":
                if self.queue_low:
                    prueba2(self, self.queue_low, free_daemons, "LOW")
                    despachado = True
                else:
                    print("@@No hay nada en la lista de prioirdad baja, cambiamos politica,vamos alta")
                    self.politica = "HIGH"
        else:
            if not despachado:
                print("No hay tareas pendientes", self.politica)
                print(self.queue_high)
    else:
        print("No hay demonios disponibles")


def prueba2(self, queue, free_daemons, prioridad):
    for _ in range(len(queue)):
        tipo_daemon = queue[0]['tipo_daemon']
        if tipo_daemon == 1 and 1 in free_daemons:
            get_free_daemon = freeDaemon(self.t1_daemons)
            if get_free_daemon != -1:
                print("Daemon tipo 1 se le envia el trabajo", get_free_daemon)
                encargoDaemon(self, prioridad, get_free_daemon, tipo_daemon)
                self.t1_daemons[get_free_daemon].status = "BUSY"  # Para evitar errores
                # Revisa si hay mas libres aparte de el, cambia a false si no hay
                check_daemons(self, 1)
            else:  # No hay demonios disponibles
                self.status_daemons[0] = False
                print(free_daemons)
                print("Ya no hay demonios tipo 1")
                break
        elif tipo_daemon == 2 and 2 in free_daemons:
            get_free_daemon = freeDaemon(self.t2_daemons)
            if get_free_daemon != -1:
                print("Daemon tipo2 se le envio el trabajo:", get_free_daemon)
                encargoDaemon(self, prioridad, get_free_daemon, tipo_daemon)
                self.t2_daemons[get_free_daemon].status = "BUSY"
                check_daemons(self, 2)
            else:
                self.status_daemons[1] = False
                print("Ya no hay demonios tipo 2")
        elif tipo_daemon == 3 and 3:  # in free_daemons:
            # El demonio tipo 3 siempre esta disponible
            # todo: Solo deberia de hacer referencia a un demonio tipo 3
            get_free_daemon = freeDaemon(self.t3_daemons)  # SOlo hay un demonio tipo 3
            print("Daemon tipo 3 se le envio el trabajo:", get_free_daemon)
            encargoDaemon(self, prioridad, get_free_daemon, tipo_daemon)
            # if get_free_daemon != -1:
            #     print("Daemon tipo 3 se le envio el trabajo:", get_free_daemon)
            #     encargoDaemon(self, prioridad, get_free_daemon, tipo_daemon)
            #     self.t3_daemons[get_free_daemon].status = "BUSY"
            #     check_daemons(self, 3)
            # else:
            #     self.status_daemons[2] = False
            #     print("Ya no hay demonios tipo 3")
        # else:
        #     print("Algo malo paso, ver linea 143")
        #     break
        contPrioridad(self, prioridad)


def contPrioridad(self, prioridad):
    """ Revisa si se tiene que cambiar la polica de priridad
    basado en los contadores
    """
    if prioridad == "HIGH" and self.cont_prioridad_alta > PRIORIDAD_ALTA:
        self.cont_prioridad_alta = 0
        print("CAMBIO!!! a medium por politica")
        self.politica = "MEDIUM"
    elif prioridad == "MEDIUM" and self.cont_prioridad_media > PRIORIDAD_MEDIA:
        self.cont_prioridad_media = 0
        self.poltica = "LOW"
    elif prioridad == "LOW" and self.cont_proridad_baja > PRIORIDAD_BAJA:
        self.cont_proridad_baja = 0
        self.politica = "HIGH"


resultado_ids = [['Copy 1'], ['Copy 2'], ['Copy 3']]


def add_result(self, id, contenido):
    global resultado_ids
    if id == 'all':
        for elemento in range(len(resultado_ids)):
            if contenido in resultado_ids[elemento]:
                break
            else:
                resultado_ids[elemento].append(f'[{self.clock}]: {contenido}')
    else:
        resultado_ids[id].append(f'[{self.clock}]: {contenido}')
    print(f'[{self.clock}]: {contenido}')


general = []


def add_global_result(self, contenido):
    global general
    general.append(f"[{self.clock}]: {contenido}")
    print(f'[{self.clock}]: {contenido}')
    return general
