import random
import math
import copy
import uuid
from .salidas import add_all, add_result, Config
from .memento import ConcreteMemento, Caretaker, Memento
from .mensajes import store, insert, report, confirmStorage, confirmReport, kill_clone
from .auxiliar import (
    generateNewName,
    invokeOracle,
    encolar,
    getIndexPositions,
    encargoDaemon,
    check_daemons,
    freeDaemon,
    contPrioridad
)


class Cliente:
    def __init__(self):
        self._state = None
        pass

    @staticmethod
    def store(nodo_info):
        destino = random.randint(Config.NODO_PROXY_LOWER, Config.NODO_PROXY_UPPER)  # ID del nodo
        # Los parametros vienen del cliente
        parametros = ["file", "file_name"]
        store(nodo_info, parametros, destino)
        add_all(nodo_info, f'Mando Store al Proxy:{destino}')

    def retrive(self):
        pass

    @staticmethod
    def confirm(nodo_info, event):
        add_all(nodo_info, f"LLego la confirmacion de mi storage", "cliente")

    def save(self) -> ConcreteMemento:
        # todo: Cuando se modifica el estado?
        self._state = "State de cliente"
        return ConcreteMemento(self._state)

    def restore(self, memento: Memento):
        self._state = memento.get_state()
        # todo: Igualar todos las propiedades necesarias


class Proxy:
    def __init__(self):
        self._state = None

        # Cada que llega guarda el id_file y el nodo_id, sin importar si ya se guardo antes en algun copy
        self.record = {'id_file': [], 'nodo_id': []}
        # Aqui solo hay un unico id_file
        self.cont_copies = {'id_file': [], 'copies_store': []}

    @staticmethod
    def store(nodo_info, event):
        add_all(nodo_info, "##Proxy")
        add_all(nodo_info, f'Proxy de: {nodo_info.id}, uso buffer')
        file_, file_name = event.parametros
        new_name = generateNewName(file_name)
        parametros = [file_, new_name, Config.NUM_COPIES]  # FileID es NewName
        store(nodo_info, parametros, nodo_info.id)  # Para buffer

    def confirm(self, nodo_info, event):
        # EL resultado viene en event.operacion
        add_result(nodo_info, event.parametros['id_copy'], f"LLego confirmacion a Proxy, hago update", "proxy")
        if event.operacion == "SUCESS":
            # Buscamos si ya teniamos registro del id_file anteriormente
            for file in self.cont_copies['id_file']:
                if file == event.parametros['id_file']:
                    # No es el primer copy que llega. Se aumenta el cotador
                    index = self.cont_copies['id_file'].index(file)
                    self.cont_copies['copies_store'][index] += 1
                    if self.cont_copies['copies_store'][index] >= Config.CONFIRM_COPIES:
                        confirmReport(nodo_info, "SUCESS", nodo_info.id, "cliente")
                    break
            else:
                self.cont_copies['id_file'].append(event.parametros['id_file'])
                self.cont_copies['copies_store'].append(1)
                # Realmente entra a este if solo si Config.CONFIRM_COPIES es igual a cero.
                if self.cont_copies['copies_store'][-1] >= Config.CONFIRM_COPIES:
                    confirmReport(nodo_info, "SUCESS", nodo_info.id, "cliente")
            self.record['id_file'].append(event.parametros['id_file'])
            self.record['nodo_id'].append(event.nodo_objetivo)

    @staticmethod
    def retrive():
        pass

    def save(self) -> ConcreteMemento:
        # todo: Cuando se modifica el estado?
        self._state = "State de Proxy"
        return ConcreteMemento(self._state)

    def restore(self, memento: Memento):
        self._state = memento.get_state()
        # todo: Igualar todos las propiedades necesarias


class Buffer:
    def __init__(self, buffer_id):
        self.__buffer_id = buffer_id
        self.clones_pendientes = list()
        self.operaciones_pendientes = list()
        self._state = None
        self.files = list()
        # self.resultados = True # ya me llegaron los resultados? ver store_from_t1daemon

    @property
    def buffer_id(self):
        return self.__buffer_id

    @staticmethod
    def store_from_proxy(nodo_info, event):
        file_, new_name, num_copy = event.parametros
        for copia in range(num_copy):
            id_nodo = invokeOracle()
            add_result(nodo_info, copia, "##Buffer##", "buffer")
            add_result(nodo_info, copia,
                       f'Id del nodo regresado por oraculo: {id_nodo}', "buffer")
            parametros = {
                'file': file_,
                'id_file': new_name,
                'id_copy': copia,
                'reported': 0
            }
            insert(nodo_info,  # Para qManager
                   "T1DaemonID",
                   nodo_info.id,
                   nodo_info.id,
                   parametros,
                   "HIGH",
                   "STORE",
                   nodo_objetivo=id_nodo
                   )

    @staticmethod
    def report_from_t1daemon(nodo_info, event):
        add_result(nodo_info, event.parametros['id_copy'], "##Buffer##", "buffer")
        if event.name == "FAILURE" and event.parametros["reported"] < Config.MAX_FAILURES:
            add_result(nodo_info, event.parametros['id_copy'],
                       f"La operacion {event.operacion} fallo, lo intentamos de nuevo", "buffer")
            insert(nodo_info,
                   "T1DaemonId",
                   nodo_info.id,
                   nodo_info.id,
                   event.parametros,
                   event.prioridad,
                   event.operacion,
                   event.nodo_objetivo
                   )
        else:
            if event.name == "SUCESS":
                add_result(nodo_info, event.parametros["id_copy"], f"Operacion {event.operacion} exitosa", "buffer")
            else:  # event.parametros["reported"] > Config.MAX_FAILURES
                add_result(nodo_info, event.parametros["id_copy"], f"Operacion {event.operacion} FAILURE", "buffer")
            event.parametros['resultado'] = "SUCESS"
            # confirmStorage(nodo_info, event.operacion, nodo_info.id, "proxy", event.parametros, event.nodo_objetivo)
            confirmReport(nodo_info, event.name, nodo_info.id, "proxy", event.parametros, event.nodo_objetivo)
            # update()  # TODO: Update, actualiza la lista del buffer segun IDFILE e idCopy

    def confirm(self, nodo_info, event):
        add_result(nodo_info, event.parametros['id_copy'], "##Buffer##", "buffer")
        if event.source_element == 't2daemon':
            add_result(nodo_info, event.parametros['id_copy'], "Llego resultado de la dispersion", "buffer")
            # Matamos al clon
            if event.parametros['id_clone'] in self.clones_pendientes:
                print("Llego el restulado de la dispersion")
                kill_clone(nodo_info,
                           {'id_clone': event.parametros['id_clone'], 'id_copy': event.parametros['id_copy']},
                           "buffer",
                           self.__buffer_id)
                self.clones_pendientes.remove(event.parametros['id_clone'])
            else:
                print(f"Parametros:{event.parametros}")
                print("Ya se habia confirmado esta dispersion")
                print(f"CLones: {self.clones_pendientes}")
                print()

    # @staticmethod
    def store_from_t1daemon(self, nodo_info, event):
        clone = 0
        add_result(nodo_info, event.parametros['id_copy'], f'##Buffer##', "buffer")
        add_result(nodo_info, event.parametros['id_copy'],
                   f'Tengo que hacer un {event.operacion} a peticion de T1Daemon: {event.source_element_id} del nodo {event.source}',
                   "buffer")

        if event.parametros['id_copy'] == 0:
            add_result(nodo_info, event.parametros['id_copy'],
                       f"Ya esta guardado en el buffer, no hay riesgo de que se pierda.", "buffer")
            confirmStorage(nodo_info,
                           event.operacion,
                           event.source,
                           "t1daemon",
                           event.parametros,
                           nodo_info.id,  # Nodo objetivo, soy yo mismo
                           event.source_element_id
                           )  # Lo regreso a quien me lo mando

        elif event.parametros['id_copy'] == 1 or ('new_id_copy' in event.parametros):
            clone += 1
            add_result(nodo_info, event.parametros['id_copy'], "Voy a dispersar", "buffer")
            self.process(nodo_info, event)

        elif event.parametros["id_copy"] > 1 or clone >= 2:
            add_result(nodo_info, event.parametros['id_copy'], "Mando instruccion para crear clon", "buffer")
            parametros = copy.copy(event.parametros)
            parametros['new_id_copy'] = 1
            # Porque si no se elimina, lo tomaria como si ya lo hubiera iniciado un t1Daemmon, dentro de si mismo.
            del (parametros['timer_state'])
            # Creamos el id del clon y guardamos registro de el para poder eliminarlo despues
            parametros['id_clone'] = uuid.uuid4()
            self.clones_pendientes.append(parametros['id_clone'])
            insert(nodo_info,
                   "T3DaemonID",
                   nodo_info.id,
                   nodo_info.id,
                   parametros,
                   "HIGH",
                   "STORE",
                   elemento_interno_id=self.buffer_id,
                   nodo_objetivo=nodo_info.id,  # Nodo objetivo, soy yo mismo. El oraculo me escogio
                   timer=Config.CLONE_TIMER,
                   charge_daemon="t1daemon"
                   )

    @staticmethod
    def store_from_t2daemon(nodo_info, event):
        add_result(nodo_info, event.parametros['id_copy'],
                   f"Llego {event.name} de algun t2Daemon. Le mando confirmacion", "buffer")
        confirmStorage(nodo_info, event.name, event.source, "t2daemon",
                       event.parametros, daemon_id=event.source_element_id)

    def save(self) -> ConcreteMemento:
        # todo: Cuando se modifica el estado?
        self._state = "state de buffer"
        return ConcreteMemento(self._state)

    def restore(self, memento: Memento):
        self._state = memento.get_state()
        # todo: Igualar todos las propiedades necesarias

    def process(self, nodo_info, event):
        # File size is ramdom, for now.
        # Esta procesando un fragmento o un archivo
        contador = 0
        if 'fragment' in event.parametros:
            file_size = event.parametros['fragment']
        else:
            file_size = 5  # random.randint(1, 10)
        if file_size > Config.UMA:
            cortar = file_size / 2
            fragmentos = [file_size / cortar for _ in range(int(math.ceil(cortar)))]
        else:
            fragmentos = [file_size]
        print(f"{fragmentos}")
        for fragmento in range(len(fragmentos)):
            if fragmento > Config.UMA:
                parametros = {
                    'file': event.parametros['file'],
                    'id_file': event.parametros['id_file'],
                    'id_copy': event.parametros['id_copy'],
                    'reported': 0,
                    'fragment': fragmento,
                    'fragment_name': id(fragmento),
                    'Frag_num_copy': contador
                }
                contador += 1
                id_nodo = invokeOracle()
                insert(nodo_info,
                       "T1DaemonID",
                       nodo_info.id,
                       nodo_info.id,
                       parametros,
                       "HIGH",
                       "PROCESS",
                       nodo_objetivo=id_nodo)
            else:
                dispersos = self.disperse(fragmento)
                for disperso in range(len(dispersos)):
                    id_nodo = invokeOracle()
                    parametros = copy.copy(event.parametros)
                    parametros['disperso'] = "disperso"
                    parametros['disperso_id'] = id(disperso)
                    parametros["NewNumCopy"] = disperso
                    insert(nodo_info,
                           "T2DaemonID",
                           nodo_info.id,
                           nodo_info.id,
                           parametros,
                           "HIGH",
                           "STORE",
                           elemento_interno_remitente="buffer",
                           nodo_objetivo=id_nodo,
                           elemento_interno_id=self.buffer_id,
                           taskReplica=0
                           )
                    # insert to t2daemon

    @staticmethod
    def disperse(fragmento):
        return [fragmento / 2, fragmento / 2]


class QManager:
    def __init__(self):
        self._state = None
        self.queue_high = [[] for __ in range(0)]  # todo:Cambiar por algo mas sencillo
        self.queue_medium = [[] for __ in range(0)]
        self.queue_low = [[] for __ in range(0)]

        # Contador para politicas de servicio
        self.cont_prioridad_alta = 0
        self.cont_prioridad_media = 0
        self.cont_prioridad_baja = 0
        self.politica = "HIGH"
        self.status_daemons = [True, True, True]

    def store(self, nodo_info, event, tipo_daemon):
        add_result(nodo_info, event.parametros['id_copy'], "#QManager#", "qmanager")
        add_result(nodo_info, event.parametros['id_copy'], f'La prioridad es: {event.prioridad}', "qmanager")
        elementos = {
            'tipo_daemon': tipo_daemon,
            'nodo_objetivo': event.nodo_objetivo,
            'source': event.source,
            'operacion': event.operacion,
            'parametros': event.parametros,
            'id_daemon_objetivo': event.target_element_id
        }
        encolar(self, elementos, event.prioridad)
        add_result(nodo_info, event.parametros['id_copy'], f"Deberia encolar deamon tipo {tipo_daemon}", "qmanager")

    def retrieve_t1daemon(self):
        pass

    def process_t1daemon(self):
        pass

    def eliminate_copy(self):
        pass

    def free(self, nodo_info, daemon_id, tipo_daemon):
        pass

    def daemon_do(self, nodo_info, id_copy=None):
        if True in self.status_daemons:
            despachado = False
            while (self.queue_high or self.queue_medium or self.queue_low) and not despachado:
                free_daemons = getIndexPositions(self.status_daemons, True)
                if self.politica == "HIGH":
                    if self.queue_high:
                        prueba(self, nodo_info, self.queue_high, free_daemons, "HIGH", id_copy)
                        despachado = True
                    else:  # NO HAY NADA EN LA LISTA DE PRIORIDAD ALTA, CAMBIAMOS POLITICA
                        add_result(nodo_info, id_copy,
                                   "No hay nada en la lista de prioridad alta, cambioamos politica, vamos a media")
                        self.politica = "MEDIUM"
                if self.politica == "MEDIUM":
                    if self.queue_medium:
                        prueba(self, nodo_info, self.queue_medium, free_daemons, "MEDIUM", id_copy)
                        despachado = True
                    else:
                        add_result(nodo_info, id_copy,
                                   "No hay nada en la lista de prioridad media, cambioamos politica, vamos a baja")
                        self.politica = "LOW"
                if self.politica == "LOW":
                    if self.queue_low:
                        prueba(self, nodo_info, self.queue_low, free_daemons, "LOW", id_copy)
                        despachado = True
                    else:
                        add_result(nodo_info, id_copy,
                                   "No hay nada en la lista de prioridad baja, cambioamos politica, vamos a alta")
                        self.politica = "HIGH"
            else:
                pass
                # add_all(nodo_info, f'No hay tareas pendientes: {self.politica}')
        else:
            add_all(nodo_info, "No hay demonios disponibles")

    def save(self) -> ConcreteMemento:
        # todo: Cuando se modifica el estado?
        self._state = "state de qmanager"
        return ConcreteMemento(self._state)

    def restore(self, memento: Memento):
        self._state = memento.get_state()
        # todo: Igualar todos las propiedades necesarias


def prueba(self, nodo_info, queue, free_daemons, prioridad, id_copy):
    for iterador in range(len(queue)):
        # Revisamos el primer elementos en la cola
        tipo_daemon = queue[iterador]['tipo_daemon']
        if tipo_daemon == 1 and 1 in free_daemons:
            if queue[iterador]['id_daemon_objetivo'] is not None:
                # Quiere decir que el insert lo hizo un daemon hacia si mismo.
                index_daemon = queue[iterador]['id_daemon_objetivo']
                if nodo_info.t1_daemon[index_daemon].status == "FREE":
                    encargoDaemon(self, nodo_info, prioridad, index_daemon, id_copy)
                    break
                else:  # No esta disponible el daemon, vamos al siguiente elemento de la cola
                    print(
                        f"No esta disponible el T1daemon {queue[iterador]['id_daemon_objetivo']}, clock: {nodo_info.clock}")
                    continue
            else:
                get_free_daemon = freeDaemon(nodo_info.t1_daemons)
                if get_free_daemon != -1:
                    add_result(nodo_info, id_copy, f'Se envia trabajo al T1Daemon: {get_free_daemon}', "qmanager")
                    encargoDaemon(self, nodo_info, prioridad, get_free_daemon, id_copy)
                    nodo_info.t1_daemons[get_free_daemon].status = "BUSY"  # Para evitar errores
                    # Revisa si hay mas libres aparte de el, cambia a false si no hay
                    check_daemons(self, nodo_info, 1)
                    break
                else:  # No hay demonios disponibles
                    self.status_daemons[0] = False
                    add_result(nodo_info, id_copy, f'{free_daemons}', "qmanager")
                    add_result(nodo_info, id_copy, "Ya no hay T1Daemons", "qmanager")
                    continue
        elif tipo_daemon == 2 and 2 in free_daemons:
            if queue[iterador]['id_daemon_objetivo'] is not None:
                # Quiere decir que el insert lo hizo un daemon hacia si mismo.
                index_daemon = queue[iterador]['id_daemon_objetivo']
                if nodo_info.t2_daemons[index_daemon].status == "FREE":
                    encargoDaemon(self, nodo_info, prioridad, index_daemon, id_copy)
                    break
                else:  # No esta disponible el daemon, vamos al siguiente elemento de la cola
                    print(f"No esta disponible el T2daemon {queue[iterador]['id_daemon_objetivo']}")
                    continue
            else:
                get_free_daemon = freeDaemon(nodo_info.t2_daemons)
                if get_free_daemon != -1:
                    add_result(nodo_info, id_copy, f'Se envia trabajo al T2Daemon: {get_free_daemon}', "qmanager")
                    encargoDaemon(self, nodo_info, prioridad, get_free_daemon, id_copy)
                    nodo_info.t2_daemons[get_free_daemon].status = "BUSY"
                    check_daemons(self, nodo_info, 2)
                    break
                else:
                    self.status_daemons[1] = False
                    add_result(nodo_info, id_copy, "Ya no hay T2Daemons", "qmanager")
                    continue
        elif tipo_daemon == 3 and 3:
            # El demonio tipo 3 siempre esta disponible
            get_free_daemon = freeDaemon(nodo_info.t3_daemons)  # SOlo hay un demonio tipo 3
            add_result(nodo_info, id_copy, f'Se envia trabajo al T3Daemon: {get_free_daemon}', "qmanager")
            encargoDaemon(self, nodo_info, prioridad, get_free_daemon, id_copy)
            break
        contPrioridad(self, prioridad)


