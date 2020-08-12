
"""
Junta todas las constantes del sistema.
Esta por separado para evitar importes circulares para el caso especial de
Globals
"""


class Globals(object):
    """Proporciona la variable global que se utilizara para mandar al contexto de la GUI
    y la manipulacion de la variable se definen en auxiliar.py"""
    resultado_ids = [['Copy 1'], ['Copy 2'], ['Copy 3']]

    # @staticmethod
    # def clear():
    #     resultado_ids = [['Copy 1'], ['Copy 2'], ['Copy 3']]


class Config(object):
    """Constantes necesarias para el algoritmo, si se quiere modificar el comportamiento
        aqui se modifican la constantes necesarias. 
    """
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


    T1_DAEMONS = 5    # Numero de dameons tipo 1
    T1_MAX_COUNT = 1  # Numero de intentos del timer t1Daemon
    
    T2_DAEMONS = 5    # Numero de daemon tipo 2

    # T3Daemon Solo hay 1 daemon tipo 3
    T3_DAEMONS = 1

    # Numero de buffers
    BUFFERS = 5
