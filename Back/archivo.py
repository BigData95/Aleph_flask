class Archivo:
    def __init__(self, file_, name, new_name, num_copies):
        """ No deberia cambiar ningun atributo una vez creado"""
        self.__file_ = file_
        self.__name = name
        self.__new_name = new_name
        self.__num_copies = num_copies

    @property
    def file_(self):
        return self.__file_

    @property
    def name(self):
        return self.__name

    @property
    def new_name(self):
        return self.__new_name

    @property
    def num_copies(self):
        return self.__num_copies


class Copy:
    def __init__(self, id_file, id_copy, id_nodo, reported=0):
        """Siempre asociados a algun Archivo, no pueden existir por si solos"""
        self.__id_file = id_file
        self.__id_copy = id_copy
        self.__id_nodo = id_nodo
        self.__reported = reported

    @property
    def id_file(self):
        return self.__id_file

    @property
    def id_copy(self):
        return self.__id_copy

    @property
    def id_nodo(self):
        return self.__id_nodo

    @property
    def reported(self):
        return self.__reported

    @reported.setter
    def reported(self, nuevo):
        self.__reported = nuevo


