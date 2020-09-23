# Este archivo contiene la implementacion de la clase Event (11.11.10)
""" Un objeto de la clase Event encapsula la informacion que se intercambia 
entre las entidades activas de un sistema distribuido """


# ----------------------------------------------------------------------------------------


class Event:  # Descendiente de la clase "object" (default)
    """ Atributos: "name", "time", "target" y "source", 
    contiene tambien un constructor y los metodos que devuelven cada
    uno de los atributos individuales """

    def __init__(self, name, time, target, source, port=0):
        """ Construye una instancia con los atributos inicializados """
        self.__name = name
        self.__time = time
        self.__target = target
        self.__source = source
        self.__port = port

    @property
    def name(self):
        return self.__name

    @property
    def time(self):
        return self.__time

    @property
    def target(self):
        return self.__target

    @property
    def source(self):
        return self.__source

    @property
    def port(self):
        return self.__port

    # def getName(self):
    #     """ Devuelve el nombre del evento """
    #     return self.__name

    # def getTime(self):
    #     """ Devuelve el tiempo en el que debe ocurrir el evento """
    #     return self.__time

    # def getTarget(self):
    #     """ Devuelve la identidad del proceso al que va dirigido """
    #     return self.__target

    # def getSource(self):
    #     """ Devuelve la identidad del proceso que origina el evento """
    #     return self.__source

    # def getPort(self):
    #     """ Devuelve el puerto al que va dirigido """
    #     return self.__port
