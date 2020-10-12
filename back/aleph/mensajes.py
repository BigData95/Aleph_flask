from back.simulador.event import Event


# from .salidas import add_result, add_all


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

    def __init__(self,
                 name,
                 time,
                 target,
                 source,
                 parametros=None,
                 operacion=None,
                 elemento_interno_objetivo=None,
                 elemento_interno_remitente=None,
                 elem_int_obj_id=None,
                 elem_int_rem_id=None,
                 nodo_objetivo=None,
                 prioridad=None,
                 lista_fallo=None,
                 tiempo_fallo=None,
                 tiempo_recuperacion=None,
                 #  puerto=0
                 ):
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
            ):
    """ Mandar mensajer completos
        Los parametros con valores por default pueden ser prescindibles en algunos mensajes especificos
        de esta forma cuando se hace uso del metodo y se necesita algun parametro con valores con default(pero no todos)
        se debe de especificar en la llamada del metodo, haciendo mas legible el codigo, ejemplo:
            mensaje(self,name,target,source,parametros,operacion="STORE",nodo_objetivo=2)

        Recordar: Se tiene que seguir el orden de los parametros como estan definidos arriba.
            mensaje(self,name,target,source,parametros,nodo_objetivo=2,operacion="STORE") es incorrecto.
    """
    newevent = Mensaje(name,
                       self.clock + 1.0,
                       target,
                       source,
                       parametros,
                       operacion,
                       elemento_interno_objetivo,
                       elemento_interno_remitente,
                       elem_int_obj_id,
                       elem_int_rem_id,
                       nodo_objetivo,
                       prioridad
                       )
    self.transmit(newevent)


def execute(self, target_nodo, source, operacion, parametros, prioridad, daemon_id, tipo_daemon, id_daemon_objetivo):
    if tipo_daemon == 1:
        mensaje(self,
                "EXECUTE",
                self.id,
                source,
                parametros,
                operacion,
                "t1daemon",
                "qmanager",
                target_nodo,
                prioridad,
                daemon_id,
                id_daemon_objetivo
                )
    if tipo_daemon == 2:
        mensaje(self,
                "EXECUTE",
                self.id,
                source,
                parametros,
                operacion,
                "t2daemon",
                "qmanager",
                target_nodo,
                prioridad,
                daemon_id,
                id_daemon_objetivo
                )
    if tipo_daemon == 3:
        mensaje(self,
                "EXECUTE",
                self.id,
                source,
                parametros,
                operacion,
                "t3daemon",
                "qmanager",
                target_nodo,
                prioridad,
                daemon_id,
                id_daemon_objetivo
                )


# Timer de t1Daemon
def startTimer(self, parametros, operacion, daemon_id, nodo_objetivo, prioridad, tipo_daemon, timer_value=1):
    # No confundir con el metodo "mensaje", en ese metodo no puedes manipular el tiempo en el que se manda.
    newEvent = Mensaje("TIMER",
                       self.clock + timer_value,
                       self.id,
                       self.id,
                       parametros,  # parametros
                       operacion,
                       tipo_daemon,
                       tipo_daemon,
                       daemon_id,
                       daemon_id,
                       nodo_objetivo,
                       prioridad
                       )
    # Parametros: --> [newFileName, IdCopia,[result,reported],state]
    self.transmit(newEvent)


# def startTimer2()


def startTimerClone(self, timer_value, operacion, parametros, daemon_id):
    newEvent = Mensaje("TIMER_CLONE",
                       self.clock + timer_value,
                       self.id,
                       self.id,
                       parametros,
                       operacion,  # Operacion
                       "t3daemon",
                       "t3daemon",
                       daemon_id,
                       daemon_id
                       )
    self.transmit(newEvent)


# Manda T1 a nodo target
def invokeTask(self, target, operacion, parametros, daemon_id, tipo_daemon):
    mensaje(self,
            "TASK",
            target,
            self.id,
            parametros,
            operacion,
            "buffer",
            tipo_daemon,
            nodo_objetivo=target,
            elem_int_rem_id=daemon_id
            )
    if operacion == "ELIMINATECOPY":  # Manda al proxy
        pass


# Siempre es para el qmanager
def insert(self,
           daemon,
           source,
           target,
           parametros,
           prioridad,
           operacion,
           elemento_interno_remitente="buffer",
           nodo_objetivo=None,
           timer=None,
           taskReplica=None,
           charge_daemon=None,
           daemon_id=None
           ):
    # !TODO: daemon_id y elemento_interno_id es lo mismo

    if daemon == "T1DaemonID":
        mensaje(self,
                daemon,
                target,
                source,
                parametros,
                operacion,
                "qmanager",
                elemento_interno_remitente,
                nodo_objetivo,
                prioridad,
                daemon_id,
                daemon_id
                )
    if daemon == "T3DaemonID":
        parametros['timer'] = timer
        parametros['charge_daemon'] = charge_daemon
        newevent = Mensaje(daemon,
                           self.clock + timer,
                           target,
                           source,
                           parametros,
                           operacion,
                           "qmanager",
                           elemento_interno_remitente,
                           daemon_id,
                           daemon_id,
                           nodo_objetivo,
                           prioridad
                           )
        self.transmit(newevent)

    if daemon == "T2DaemonID":
        if 'taskReplica' not in parametros:
            parametros['taskReplica'] = taskReplica
        mensaje(self,
                daemon,
                target,
                source,
                parametros,
                operacion,
                "qmanager",
                elemento_interno_remitente,
                nodo_objetivo,
                prioridad,
                daemon_id,
                daemon_id
                )


def store(self, parametros, target):
    # Viene del cliente
    if len(parametros) < 3:
        mensaje(self,
                "STORE",
                target,
                self.id,
                parametros,
                elemento_interno_objetivo="proxy"
                )
    # Viene del Proxy
    else:
        mensaje(self,
                "STORE",
                target,
                self.id,
                parametros,
                elemento_interno_objetivo="buffer",
                elemento_interno_remitente="proxy"
                )


# TODO:Tiene que ser para todos los daemons, no solo t1daemon
def mensajeDaemon(self, name, daemon_id, tipo_operacion, tipo_daemon, id_copy):
    mensaje(self,
            name,
            self.id,
            self.id,
            {'id_copy': id_copy},
            tipo_operacion,  # operacion
            "qmanager",
            tipo_daemon,
            elem_int_obj_id=daemon_id  # elem_int_obj_id
            )


# TODO: Esta escrtio para t1Daemon, quiza se deba tomar en cuenta los demas
def report(self, result, daemon_id, parameters, nodo_objetivo, prioridad=None, operacion=None, ):
    mensaje(self,
            result,
            self.id,
            self.id,
            parameters,
            operacion,
            "buffer",
            "t1daemon",
            nodo_objetivo,
            prioridad,
            elem_int_rem_id=daemon_id,
            )


# ConfirmStorage siempre regresa sucess
def confirmStorage(self, operacion, destino, destino_interno, parametros=None, nodo_objetivo=None, daemon_id=None,
                   remitente_interno=None, remitente_interno_id=None):
    # ConfirmStorage siempre tiene resultado sucess, menos cuando va del buffer al proxy
    # y cuando va desl Proxy al cliente, pues te da el resultado, hace un nuevo metodo
    mensaje(self,
            "CONFIRM",
            destino,  # id del nodo
            self.id,
            parametros,
            operacion,
            elemento_interno_objetivo=destino_interno,
            elemento_interno_remitente=remitente_interno,
            nodo_objetivo=nodo_objetivo,
            elem_int_obj_id=daemon_id,
            elem_int_rem_id=remitente_interno_id
            )


def confirmReport(self, resultado, destino, destino_interno, parametros=None, nodo_objetivo=None):
    mensaje(self,
            "CONFIRM",
            destino,
            self.id,
            parametros,
            resultado,
            destino_interno,
            nodo_objetivo=nodo_objetivo,
            )


def kill_clone(self, clone_id, source_element, source_element_id):
    mensaje(self,
            "KILL",
            self.id,
            self.id,
            clone_id,  # Parametros incluyen id_clone e id_copy
            elemento_interno_objetivo='t3daemon',
            elemento_interno_remitente=source_element,
            elem_int_obj_id=0,
            elem_int_rem_id=source_element_id
            )

# # Tiene un resultado: SUCESS or FAILURE
# def reportResults(self, resultado, destino, destino_interno):
#     print("Si se hace el report")
#     mensaje(self,
#             resultado,
#             destino,
#             self.id,
#             None,
#             elemento_interno_objetivo=destino_interno
#             )
