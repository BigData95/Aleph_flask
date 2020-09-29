# Este archivo contiene la implementacion de la clase Model (11.11.10)
""" No se pueden generar instancias de esta clase. Se usa para comprometer al 
programador a proporcionar, en una clase descendiente, la implementacion de 
los metodos o propiedades etiquetados como abstractos. Este es el mecanismo 
para programar una aplicacion, i.e. un algoritmo concreto """

# ----------------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod


class Model(metaclass=ABCMeta):
    """ Atributos: "clock", "process", "neighbors", "id",
    contiene tambien un constructor y los metodos "setProcess()",
    "transmit()", "init()" y "receive()", estos dos ultimos son
    metodos abstractos que deben implementarse en la aplicacion """

    # __metaclass__ = ABCMeta
    @abstractmethod
    def __init__(self):
        """ define el valor inicial de su reloj """
        self.clock = 0.0
        
        # Es buena practica poner todos los atributos dentro del init. Aunque no se inicialicen ahi
        # Quiza setProcess deberia ser el verdadero __init__.
        self.process = None
        self.neighbors = None
        self.id = None
        self.port = None

    def setTime(self, time):
        """ actualiza el valor del reloj local """
        self.clock = time

    def setProcess(self, process, neighbors, id, port=0):
        """ asocia al modelo con su entidad activa (proceso), su lista 
        de vecinos y su identificador """
        self.process = process
        self.neighbors = neighbors
        self.id = id
        self.port = port

    def transmit(self, event):
        """ invoca el metodo de transmision de su entidad activa (proceso) """
        self.process.transmit(event)

    # @abstractmethod
    def init(self):
        """ Que se inicializa? eso se define en la aplicacion """
        pass

    @abstractmethod
    def receive(self, event):
        """ Que se hace con un evento recibido? eso se define la aplicacion """
        pass
