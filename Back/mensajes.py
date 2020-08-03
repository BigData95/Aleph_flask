from .simulador.event import Event


class Mensaje(Event):
    """ Modifica la clase Event para agregar mas parametros necesarios para el algoritmo

    Atributos:
        name:
        operacion:
        time:
        target:
        source:
        elemento_interno_objetivo:
        elemento_interno_remitente:
        parametros:
        prioridad:
        nodo_objetivo:
        port:
        """

    # Operacion se refiere a la operacion que haran los demons
    # name es el nombre del metodo segun el diagrama
    def __init__(self, 
                name, 
                operacion, 
                time, 
                target, 
                source,
                elemento_interno_objetivo, 
                elemento_interno_remitente,
                elem_int_obj_id, 
                elem_int_rem_id,
                parametros, 
                prioridad, 
                nodo_objetivo, 
                lista_fallo,
                tiempo_fallo,
                tiempo_recuperacion,
                port=0):
        Event.__init__(self, name, time, target, source, port=0)
        # self.__puerto = port
        self.__operacion = operacion
        self.__elemento_interno_objetivo = elemento_interno_objetivo
        self.__elemento_interno_remitente = elemento_interno_remitente
        self.__elem_int_obj_id = elem_int_obj_id
        self.__elem_int_rem_id = elem_int_rem_id
        self.__parametros = parametros
        self.__prioridad = prioridad
        self.__nodo_objetivo = nodo_objetivo
        self.__lista_fallo = lista_fallo
        self.__tiempo_fallo = tiempo_fallo
        self.__tiempo_recuperacion = tiempo_recuperacion

    @property
    def operacion(self):
        return self.__operacion

    @property
    def target_element(self):
        return self.__elemento_interno_objetivo


    @property
    def source_element(self):
        return self.__elemento_interno_remitente

    @property
    def parametros(self):
        return self.__parametros

    @property
    def prioridad(self):
        return self.__prioridad

    @property
    def nodo_objetivo(self):
        return self.__nodo_objetivo

    @property
    def target_element_id(self):
        return self.__elem_int_obj_id

    @property
    def source_element_id(self):
        return self.__elem_int_rem_id
    
    @property
    def lista_fallo(self):
        return self.__lista_fallo

    @property
    def tiempo_fallo(self):
        return self.__tiempo_fallo
    
    @property
    def tiempo_recuperacion(self):
        return self.__tiempo_recuperacion


def mensaje(self, 
            name, 
            target, 
            source, 
            parametros,
            operacion=None,
            elemento_interno_objetivo=None, 
            elemento_interno_remitente=None,
            nodo_objetivo=None, 
            prioridad=None,
            elem_int_obj_id=None, 
            elem_int_rem_id=None, 
            puerto=0):
    """ Mandar mensajer completos
        Los parametros con valores por default pueden ser prescindibles en algunos mensajes especificos
        de esta forma cuando se hace uso del metodo y se necesita algun parametro con valores con default(pero no todos)
        se debe de especificar en la llamada del metodo, haciendo mas legible el codigo, ejemplo:
            mensaje(self,name,target,source,parametros,operacion="STORE",nodo_objetivo=2)

        Recordar: Se tiene que seguir el orden de los parametros como estan definidos arriba.
            mensaje(self,name,target,source,parametros,nodo_objetivo=2,operacion="STORE") es incorrecto.
    """
    newevent = Mensaje(name, 
                    operacion, 
                    self.clock + 1.0, 
                    target, 
                    source, 
                    elemento_interno_objetivo,
                    elemento_interno_remitente, 
                    elem_int_obj_id, 
                    elem_int_rem_id,
                    parametros,
                    prioridad, 
                    nodo_objetivo, 
                    None, None, None, #! CORRESPONDE A LA LISTA DE FALLOS
                    puerto
                    )
    self.transmit(newevent)


def execute(self, target_nodo, source, operacion, parametros, prioridad, daemon_id, tipo_daemon):
    if tipo_daemon == 1:
        mensaje(self, "EXECUTE", self.id, source, parametros, operacion,
                "t1daemon", "qmanager", target_nodo, prioridad, daemon_id)
    if tipo_daemon == 2:
        mensaje(self, "EXECUTE", self.id, source, parametros, operacion,
                "t2daemon", "qmanager", target_nodo, prioridad, daemon_id)
    if tipo_daemon == 3:
        mensaje(self, "EXECUTE", self.id, source, parametros, operacion,
                "t3daemon", "qmanager", target_nodo, prioridad, daemon_id)


def startTimer(self, internal_target, internal_source, timer_value=1):
    # No confundir con el metodo "mensaje", en ese metodo no puedes manipular el tiempo en el que se manda.
    newEvent = Mensaje("TIMER", 
                    "", 
                    self.clock + timer_value,
                    self.id, 
                    self.id, 
                    "t1daemon", 
                    "t1daemon",
                    internal_target, 
                    internal_source,
                    None, None, None,
                    None, None, None, #! CORRESPONDE A LA LISTA DE FALLOS
                    )  # port=0
    # Parametros: --> [newFileName, IdCopia,[result,reported],state]
    self.transmit(newEvent)


def startTimerClone(self, timer_value, tipo_daemon, clone_id, daemon_id):
    newEvent = Mensaje("TIMER", 
                    tipo_daemon, 
                    self.clock + timer_value, 
                    self.id, 
                    self.id, 
                    "t3daemon", 
                    "t3daemon",
                    daemon_id, 
                    daemon_id, 
                    None, 
                    clone_id, 
                    None,
                    None, None, None, #! CORRESPONDE A LA LISTA DE FALLOS
                    )
    self.transmit(newEvent)


# Manda T1 a nodo target
def invokeTask(self, target, operacion, parametros, daemon_id):
    if operacion == "STORE":
        mensaje(self, "STORE", target, self.id, parametros,
                operacion, "buffer", "t1daemon", nodo_objetivo=target, elem_int_rem_id=daemon_id)
        print("Soy T1 y mando a ", target)
    if operacion == "ELIMINATECOPY":  # Manda al proxy
        pass


# Siempre es para el qmanager
def insert(self, daemon, source, target, parametros, prioridad, operacion,
           elemento_interno_remitente="buffer", buffer_id=None,
           nodo_objetivo=None, timer=None, taskReplica=None, source_daemon=None, tipo_daemon=None):
    # !TODO: Verificar antipatron, targetDeamon = daemon?, verificar uso de timer y taskReplica
    if daemon == "T1DaemonID":
        print("Hago insert")
        mensaje(self, daemon, target, source, parametros, operacion,
                "qmanager", elemento_interno_remitente, nodo_objetivo, prioridad)
    if daemon == "T3DaemonID":
        parametros['timer'] = timer
        parametros['tipo_daemon'] = tipo_daemon
        mensaje(self, daemon, target, source, parametros, operacion, "qmanager",
                elemento_interno_remitente, None, prioridad, source_daemon)


def store(self, parametros, target):
    # Viene del cliente
    if len(parametros) < 3:
        mensaje(self, "STORE", target, self.id, parametros,
                elemento_interno_objetivo="proxy")
    # Viene del Proxy
    else:
        mensaje(self, "STORE", target, self.id, parametros,
                elemento_interno_objetivo="buffer", elemento_interno_remitente="proxy")


# TODO:Tiene que ser para todos los daemons, no solo t1daemon
def mensajeDaemon(self, name, daemon_id, tipo_daemon):
    newevent = Mensaje(name, 
                    tipo_daemon, 
                    self.clock + 1.0, 
                    self.id, 
                    self.id,
                    "qmanager", 
                    "t1daemon", 
                    daemon_id, 
                    None, 
                    None, 
                    None, 
                    None,
                    None, None, None, #! CORRESPONDE A LA LISTA DE FALLOS
                    )
    self.transmit(newevent)


# TODO: Esta escrtio para t1Daemon, quiza se deba tomar en cuenta los demas
def report(self, result, daemon_id, parameters, prioridad=None, operacion=None, nodo_objetivo=None):
    if result == "FAILURE":
        mensaje(self, "REPORT", self.id, self.id, parameters, operacion, "buffer", "t1daemon",
                nodo_objetivo=nodo_objetivo, prioridad=prioridad, elem_int_rem_id=daemon_id)
    else:  # resutl = SUCESS
        mensaje(self, "REPORT", self.id, self.id, parameters, operacion, "buffer", "t1daemon",
                elem_int_rem_id=daemon_id)
