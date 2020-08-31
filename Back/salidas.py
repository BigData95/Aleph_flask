"""
Junta todas las constantes del sistema y los metodos que involucran la salida al GUI
Esta por separado para evitar importes circulares. No puede importar ningun modulo
"""


class Globals:
    """Proporciona la variable global que se utilizara para mandar al contexto de la GUI
    y la manipulacion de la variable se definen mas abajo"""
    resultado_ids = [
        [['Copy 1'], ['all']],
        [['Copy 2'], ['all']],
        [['Copy 3'], ['all']]
    ]


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
        [['Copy 1'], ['all']],
        [['Copy 2'], ['all']],
        [['Copy 3'], ['all']]
    ]

    return Globals.resultado_ids


def regresa():
    return Globals.resultado_ids
