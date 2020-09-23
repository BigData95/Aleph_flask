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


def clear():
    Globals.resultado_ids = [
        [['Copy 0'], ['all']],
        [['Copy 1'], ['all']],
        [['Copy 2'], ['all']]
    ]
    return Globals.resultado_ids


def regresa():
    return Globals.resultado_ids
