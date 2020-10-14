import pathlib
from back.simulador import Simulation
from .Aleph import Aleph
from .auxiliar import toList, seed_all
from .mensajes import Mensaje
from .salidas import regresa


def inicia(lista_fallo=None, tiempo_fallo=None, tiempo_recuperacion=None, nodo_oracle_1=None, nodo_oracle_2=None, nodo_oracle_3=None):
    """
    Se llama desde app/auth/views.py
    Se hace la validacion de lista_fallo, tiempo_fallo y tiempo_recuperacion para que
    las 3 listas esten completamente vacias o las 3 listas contengan datos.
    """
    fn = pathlib.Path(__file__).parent / 'topo.txt'
    experiment = Simulation(fn, 500)
    # asocia un pareja proceso/modelo con cada nodo de la grafica
    for i in range(1, len(experiment.graph) + 1):
        m = Aleph()
        experiment.setModel(m, i)

    # ! No es necesrio hacer los 3 ifs porque desde el GUI se valida.
    # Si uno esta vacia todos lo estan, si una tiene cosas, las demas tambien.
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
    if nodo_oracle_1 is not None:
        seed = Mensaje(
            "DESPIERTA",
            0.0,  # Tiempo
            1,  # Target
            1,  # Source
            lista_fallo=lista_fallo,
            tiempo_fallo=tiempo_fallo,
            tiempo_recuperacion=tiempo_recuperacion,
            extras=[nodo_oracle_1, nodo_oracle_2, nodo_oracle_3]
        )
    else:
        seed = Mensaje(
            "DESPIERTA",
            0.0,  # Tiempo
            1,  # Target
            1,  # Source
            lista_fallo=lista_fallo,
            tiempo_fallo=tiempo_fallo,
            tiempo_recuperacion=tiempo_recuperacion
        )
    experiment.init(seed)

    # En este punto lista_fallo ya es una lista.
    if lista_fallo:
        seed_all(experiment,
                 experiment.numero_nodos,
                 "AVISO_FALLO",
                 lista_fallo,
                 tiempo_fallo,
                 tiempo_recuperacion)
    experiment.run()

    return regresa()
