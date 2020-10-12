from back.aleph.salidas import add_all, add_result
from back.aleph.memento import ConcreteMemento, Memento
from back.aleph.auxiliar import (
    encolar,
    getIndexPositions,
    encargoDaemon,
    check_daemons,
    freeDaemon,
    contPrioridad
)


class QManager:
    def __init__(self):
        self._state = None
        self.queue_high = []  # todo:Cambiar por algo mas sencillo
        self.queue_medium = []
        self.queue_low = []

        # Contador para politicas de servicio
        self.cont_prioridad_alta = 0
        self.cont_prioridad_media = 0
        self.cont_prioridad_baja = 0
        self.politica = "HIGH"
        self.status_daemons = [True, True, True]

    def store(self, nodo_info, event, tipo_daemon):
        add_result(nodo_info, event.parametros['id_copy'], "#QManager#", "qmanager")
        # add_result(nodo_info, event.parametros['id_copy'], f'La prioridad es: {event.prioridad}', "qmanager")
        elementos = {
            'tipo_daemon': tipo_daemon,
            'nodo_objetivo': event.nodo_objetivo,
            'source': event.source,
            'operacion': event.operacion,
            'parametros': event.parametros,
            'id_daemon_objetivo': event.target_element_id
        }
        encolar(self, elementos, event.prioridad)
        add_result(nodo_info, event.parametros['id_copy'], f"Encola a deamon tipo:{tipo_daemon} Prioridad:{event.prioridad}", "qmanager")

    def retrieve_t1daemon(self):
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
                        iterar_daemon(self, nodo_info, self.queue_high, free_daemons, "HIGH", id_copy)
                        despachado = True
                    else:  # NO HAY NADA EN LA LISTA DE PRIORIDAD ALTA, CAMBIAMOS POLITICA
                        add_result(nodo_info, id_copy,
                                   "No hay nada en la lista de prioridad alta, cambioamos politica, vamos a media")
                        self.politica = "MEDIUM"
                if self.politica == "MEDIUM":
                    if self.queue_medium:
                        iterar_daemon(self, nodo_info, self.queue_medium, free_daemons, "MEDIUM", id_copy)
                        despachado = True
                    else:
                        add_result(nodo_info, id_copy,
                                   "No hay nada en la lista de prioridad media, cambioamos politica, vamos a baja")
                        self.politica = "LOW"
                if self.politica == "LOW":
                    if self.queue_low:
                        iterar_daemon(self, nodo_info, self.queue_low, free_daemons, "LOW", id_copy)
                        despachado = True
                    else:
                        add_result(nodo_info, id_copy,
                                   "No hay nada en la lista de prioridad baja, cambioamos politica, vamos a alta")
                        self.politica = "HIGH"
            # else:
            #     # print("No hay tareas pendientes")
            #     add_all(nodo_info, f'No hay tareas pendientes: {self.politica}')
        else:
            add_all(nodo_info, "No hay demonios disponibles")

    def save(self) -> ConcreteMemento:
        # todo: Cuando se modifica el estado?
        self._state = "state de qmanager"
        return ConcreteMemento({
            'queue_high': self.queue_high,
            'queue_medium': self.queue_medium,
            'queue_low': self.queue_low,
            'contador_prioridad_alta': self.cont_prioridad_alta,
            'contador_prioridad_media': self.cont_prioridad_media,
            'contador_prioridad_baja': self.cont_prioridad_baja,
            'politica': self.politica,
            'status_daemons': self.status_daemons
        })
        # return ConcreteMemento(self._state)

    def restore(self, memento: Memento):
        self._state = memento.get_state()
        self.queue_high = self._state['queue_high']
        self.queue_medium = self._state['queue_medium']
        self.queue_low = self._state['queue_low']
        self.cont_prioridad_alta = self._state['contador_prioridad_alta']
        self.cont_prioridad_media = self._state['contador_prioridad_media']
        self.cont_prioridad_baja = self._state['contador_prioridad_baja']
        self.politica = self._state['politica']
        self.status_daemons = self._state['status_daemons']
        # todo: Igualar todos las propiedades necesarias


def iterar_daemon(self, nodo_info, queue: list, free_daemons: int, prioridad: str, id_copy: int):
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
                    # add_result(nodo_info, id_copy, f'Se envia trabajo al T1Daemon: {get_free_daemon}', "qmanager")
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
                    # add_result(nodo_info, id_copy, f'Se envia trabajo al T2Daemon: {get_free_daemon}', "qmanager")
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
            # add_result(nodo_info, id_copy, f'Se envia trabajo al T3Daemon: {get_free_daemon}', "qmanager")
            encargoDaemon(self, nodo_info, prioridad, get_free_daemon, id_copy)
            break
        contPrioridad(self, prioridad)
