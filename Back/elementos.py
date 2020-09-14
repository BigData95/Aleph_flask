import random
import math
import copy
from .salidas import add_all, add_result, Config
from .memento import ConcreteMemento, Caretaker, Memento
from .mensajes import store, insert, report, confirmStorage,  confirmReport
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
        print("llego la confirmacion al cliente! Cool")

    def save(self) -> ConcreteMemento:
        # todo: Cuando se modifica el estado?
        self._state = "State de cliente"
        return ConcreteMemento(self._state)

    def restore(self, memento: Memento):
        self._state = memento.get_state()
        print(f'Soy cliente y mi state es {self._state}')
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
                        # TODO: Deberia de ser reportResults
                    break
            else:
                self.cont_copies['id_file'].append(event.parametros['id_file'])
                self.cont_copies['copies_store'].append(1)
                # Realmente entra a este if solo si Config.CONFIRM_COPIES es igual a cero.
                if self.cont_copies['copies_store'][-1] >= Config.CONFIRM_COPIES:
                    confirmReport(nodo_info, "SUCESS", nodo_info.id, "cliente")
                    # TODO: Deberia de ser reportResults
            self.record['id_file'].append(event.parametros['id_file'])
            self.record['nodo_id'].append(event.nodo_objetivo)

    @staticmethod
    def retrive():
        pass

    def save(self) -> ConcreteMemento:
        # todo: Cuando se modifica el estado?
        self._state = "State de Proxy"
        print(f'Soy proxy: {self._state}')
        return ConcreteMemento(self._state)

    def restore(self, memento: Memento):
        self._state = memento.get_state()
        # todo: Igualar todos las propiedades necesarias


class Buffer:
    def __init__(self, buffer_id):
        self.__buffer_id = buffer_id
        self._state = None
        self.files = list()
        # self.resultados = True # ya me llegaron los resultados? ver store_from_t1daemon

    @property
    def buffer_id(self):
        return self.__buffer_id

    @staticmethod
    def store_from_proxy(nodo_info, event):
        # TODO: Tambien deberia funcionar para process
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
            add_result(nodo_info, event.parametros['id_copy'], "La operacion fallo, lo intentamos de nuevo", "buffer")
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

    @staticmethod
    def confirm(nodo_info, event):
        add_result(nodo_info, event.parametros['id_copy'], "##Buffer##", "buffer")
        if event.source_element == 't2daemon':
            add_result(nodo_info, event.parametros['id_copy'], "Llego resultado de la dispersion", "buffer")
            print(f"{nodo_info.id}:LLega el resultado de la dispersion, siempre sera sucess")

    def store_from_t1daemon(self, nodo_info, event):
        clone = 0
        # TODO: Store solo viene de t1Daemon, es redundate
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
        print(f"Se hace Store, mando confirmacion, va para el t2daemon: {event.source_element_id}")
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
        # File size is ramdom, for now. #TODO: maybe not randomize
        file_size = 5  # random.randint(1, 10)
        if file_size > Config.UMA:
            cortar = file_size / Config.UMA
            fragmentos = [file_size / cortar for _ in range(int(math.ceil(cortar)))]
        else:
            fragmentos = [file_size]
        print(f"Fragmentos {fragmentos}")
        for fragmento in range(len(fragmentos)):
            if fragmento > Config.UMA:
                print("Se debe hacer insert a t1Daemon")
                pass
            else:
                dispersos = self.disperse(fragmento)
                for disperso in range(len(dispersos)):
                    id_nodo = invokeOracle()
                    print(f"Soy {nodo_info.id}. Aqui debe terminar el invokeTask {id_nodo}")
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
                           nodo_objetivo=id_nodo,
                           elemento_interno_id=self.buffer_id,
                           taskReplica=0
                           )
                    # insert to t2daemon

    @staticmethod
    def disperse(fragmento):
        return [fragmento / 2, fragmento / 2]
        pass


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
        # self.wait_status = False
        self.politica = "HIGH"
        self.status_daemons = [True, True, True]

    def store(self, nodo_info, event, tipo_daemon):
        add_result(nodo_info, event.parametros['id_copy'], "#QManager#", "qmanager")
        add_result(nodo_info, event.parametros['id_copy'], f'La prioridad es: {event.prioridad}', "qmanager")
        if tipo_daemon == 1:
            elementos = {
                'tipo_daemon': tipo_daemon,
                'nodo_objetivo': event.nodo_objetivo,
                'source': event.source,
                'operacion': event.operacion,
                'parametros': event.parametros,
                'id_daemon_objetivo': event.target_element_id
            }
        else:  # tipo daemon 2
            elementos = {
                'tipo_daemon': tipo_daemon,
                'nodo_objetivo': event.target,
                'source': event.source,
                'operacion': event.operacion,
                'parametros': event.parametros,
                'id_daemon_objetivo': event.source_element_id
            }
        encolar(self, elementos, event.prioridad)
        add_result(nodo_info, event.parametros['id_copy'], f"Deberia encolar deamon tipo {tipo_daemon}", "qmanager")

    def retrieve_t1daemon(self):
        pass

    def process_t1daemon(self):
        pass

    def eliminate_copy(self):
        pass

    def free(self, nodo_info, event):
        # add_all(nodo_info, '##QManager##')
        # add_all(nodo_info, f'Se libero el daemon tipo {event.operacion}. ID:{event.target_element_id} de nodo {nodo_info.id}')
        daemon_type = int(event.operacion) - 1
        if not self.status_daemons[daemon_type]:
            print("Ya hay demonios tipo", event.operacion, "disponibles")
            self.status_daemons[daemon_type] = True

    def daemon_do(self, nodo_info, id_copy=None):
        if True in self.status_daemons:
            # print("HAY DEMONIOS")
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
            print("No hay demonios disponibles")

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
        elif tipo_daemon == 3 and 3:  # in free_daemons:
            # El demonio tipo 3 siempre esta disponible
            # todo: Solo deberia de hacer referencia a un demonio tipo 3
            get_free_daemon = freeDaemon(nodo_info.t3_daemons)  # SOlo hay un demonio tipo 3
            add_result(nodo_info, id_copy, f'Se envia trabajo al T3Daemon: {get_free_daemon}', "qmanager")
            encargoDaemon(self, nodo_info, prioridad, get_free_daemon, id_copy)
            break
        contPrioridad(self, prioridad)

# def prueba2(self, nodo_info, queue, free_daemons, prioridad, id_copy):
#     for _ in range(len(queue)):
#         tipo_daemon = queue[0]['tipo_daemon']  # Revisamos el primer elemento en la cola
#         if tipo_daemon == 1 and 1 in free_daemons:
#             # if queue[0]['id_daemon_objetivo'] is not None:
#             #     # Quiere decir que el insert lo hizo un daemon asi si mismo.
#             get_free_daemon = freeDaemon(nodo_info.t1_daemons)
#             if get_free_daemon != -1:
#                 add_result(nodo_info, id_copy, f'Se envia trabajo al T1Daemon: {get_free_daemon}', "qmanager")
#                 encargoDaemon(self, nodo_info, prioridad, get_free_daemon, id_copy)
#                 nodo_info.t1_daemons[get_free_daemon].status = "BUSY"  # Para evitar errores
#                 # Revisa si hay mas libres aparte de el, cambia a false si no hay
#                 check_daemons(self, nodo_info, 1)
#             else:  # No hay demonios disponibles
#                 self.status_daemons[0] = False
#                 add_result(nodo_info, id_copy, f'{free_daemons}', "qmanager")
#                 add_result(nodo_info, id_copy, "Ya no hay T1Daemons", "qmanager")
#                 break
#         elif tipo_daemon == 2 and 2 in free_daemons:
#             get_free_daemon = freeDaemon(nodo_info.t2_daemons)
#             if get_free_daemon != -1:
#                 add_result(nodo_info, id_copy, f'Se envia trabajo al T2Daemon: {get_free_daemon}', "qmanager")
#                 encargoDaemon(self, nodo_info, prioridad, get_free_daemon, id_copy)
#                 self.t2_daemons[get_free_daemon].status = "BUSY"
#                 check_daemons(self, nodo_info, 2)
#             else:
#                 self.status_daemons[1] = False
#                 add_result(nodo_info, id_copy, "Ya no hay T2Daemons", "qmanager")
#         elif tipo_daemon == 3 and 3:  # in free_daemons:
#             # El demonio tipo 3 siempre esta disponible
#             # todo: Solo deberia de hacer referencia a un demonio tipo 3
#             get_free_daemon = freeDaemon(nodo_info.t3_daemons)  # SOlo hay un demonio tipo 3
#             add_result(nodo_info, id_copy, f'Se envia trabajo al T3Daemon: {get_free_daemon}', "qmanager")
#             encargoDaemon(self, nodo_info, prioridad, get_free_daemon, id_copy)
#             # if get_free_daemon != -1:
#             #     print("Daemon tipo 3 se le envio el trabajo:", get_free_daemon)
#             #     encargoDaemon(self, prioridad, get_free_daemon, tipo_daemon)
#             #     self.t3_daemons[get_free_daemon].status = "BUSY"
#             #     check_daemons(self, 3)
#             # else:
#             #     self.status_daemons[2] = False
#             #     print("Ya no hay demonios tipo 3")
#         # else:
#         #     print("Algo malo paso, ver linea 143")
#         #     break
#         contPrioridad(self, prioridad)
