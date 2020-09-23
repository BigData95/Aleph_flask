# Este archivo contiene la implementacion de la clase Simulation (11.11.10)
""" Un objeto de la clase Simulation representa un experimento en el que
se ejecuta un algoritmo distribuido sobre una grafica de comunicaciones """

from .process import Process
from .simulator import Simulator
# ----------------------------------------------------------------------------------------

import re  # <-- Libreria
class Simulation:
    """ Atributos: "engine", "graph", "table", contiene tambien un
    constructor y los metodos "setModel()", "init()", "run()" """

    def __init__(self, filename, maxtime):
        lineas_vacias = re.compile('\n')
        """ construye su motor de simulacion, la grafica de comunicaciones y
        la tabla de procesos """
        self.__numero_nodos = 0  # <-- Contador

        self.engine = Simulator(maxtime)
        f = open(filename)
        lines = f.readlines()
        f.close()
        self.graph = []
        for line in lines:
            fields = line.split()
            neighbors = []
            if not lineas_vacias.match(line): #<-- Revisa si la linea comienza con el salto de linea
                self.__numero_nodos += 1   # <-- Aumenta contador
                for f in fields:
                    neighbors.append(int(f))
                self.graph.append(neighbors)

        self.table = [[]]          # la entrada 0 se deja vacia
        for i, row in enumerate(self.graph):
            newprocess = Process(row, self.engine, i+1)
            self.table.append(newprocess)

    def setModel(self, model, id, port=0):
        """ asocia al proceso con el modelo que debe ejecutar y viceversa """
        process = self.table[id]
        process.setModel(model, port)

    def init(self, event):
        """ inserta un evento semilla en la agenda """
        self.engine.insertEvent(event)

    def run(self):
        """ arranca el motor de simulacion """
        while self.engine.isOn():
            nextevent = self.engine.returnEvent()
            target = nextevent.target   # <-- Antes nextevent.getTarget()
            time = nextevent.time
            port = nextevent.port
            nextprocess = self.table[target]
            nextprocess.setTime(time, port)
            nextprocess.receive(nextevent, port)


    # <-- Aceder a property
    @property
    def numero_nodos(self): 
        return self.__numero_nodos