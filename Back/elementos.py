import random
from .salidas import add_all, add_result, Config
from .mensajes import store, insert, report
from .auxiliar import (
    generateNewName,
    update,
    confirmStorage,
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
        pass

    @staticmethod
    def store(nodo_info):
        destino = random.randint(2, 4)  # ID del nodo
        # Los parametros vienen del cliente
        parametros = ["file", "file_name"]
        store(nodo_info, parametros, destino)
        print(f'Mando Store al Proxy:{destino}')
        add_all(nodo_info, f'Mando Store al Proxy:{destino}')

    def retrive(self):
        pass


class Proxy:
    def __init__(self):
        pass
        # self.cont_prioridad_alta = 0
        # self.cont_prioridad_media = 0
        # self.cont_prioridad_baja = 0

    @staticmethod
    def store(nodo_info, event):
        add_all(nodo_info, "##Proxy")
        add_all(nodo_info, f'Proxy de: {nodo_info.id}, uso buffer')
        file_, file_name = event.parametros
        new_name = generateNewName(file_name)
        parametros = [file_, new_name, Config.NUM_COPIES]  # FileID es NewName
        store(nodo_info, parametros, nodo_info.id)  # Para buffer

    @staticmethod
    def retrive():
        pass


class Buffer:
    def __init__(self, buffer_id):
        self.buffer_id = buffer_id
        # self.resultados = True # ya me llegaron los resultados? ver store_from_t1daemon
        pass

    @staticmethod
    def store_from_proxy(nodo_info, event):
        file_, new_name, num_copy = event.parametros
        for copia in range(num_copy):
            id_nodo = invokeOracle()
            add_result(nodo_info, copia, "##Buffer##", "buffer")
            add_result(nodo_info, copia,
                       f'Id del nodo regresado por oraculo: {id_nodo}', "buffer")
            print("El id del nodo regresado por el Oraculo, es : " + str(id_nodo))
            # initiate(result = FAILURE_SUSPICION, reported=0)
            # reported = 0
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
        if event.operacion == "SUCESS" or event.parametros["reported"] >= Config.MAX_FAILURES:
            add_result(nodo_info, event.parametros["id_copy"], f"Operacion exito {event.operacion}", "buffer")
            print(f"Operacion exito {event.operacion}")
            confirmStorage(nodo_info, event.parametros["id_file"], event.parametros["id_copy"], event.name)
            update()  # TODO: Update, actualiza la lista del buffer segun IDFILE e idCopy
        else:  # Fue failure o reported < MAX_FAILURES (NO ESTOY SEGURO LOL)
            # if event.parametros["reported"] < MAX_FAILURES: Tomar en cuenta que si la operacion es FAILURE
            # en event.operacion viene la opericon que se intento en el nodo, no "FAILURE", si fue SUCESS en
            # operacion se pone SUCESS en lugar de la operacion que se intento

            # add_result(self, 'all', f"{event.parametros}")
            add_result(nodo_info, event.parametros['id_copy'], "La operacion fallo, lo intentamos de nuevo", "buffer")
            print("La operacion fallo, lo intentamos de nuevo")
            insert(nodo_info,
                   "T1DaemonId",
                   nodo_info.id,
                   nodo_info.id,
                   event.parametros,
                   event.prioridad,
                   event.operacion,
                   event.nodo_objetivo
                   )

    # @staticmethod
    def store_from_t1daemon(self, nodo_info, event):
        print("tengo que hacer un store! Mando mensaje de confirmacion a t1 daemon, o no", event.source_element_id)
        add_result(nodo_info, event.parametros['id_copy'], '##Buffer##', "buffer")
        add_result(nodo_info, event.parametros['id_copy'],
                   f'Tengo que hacer un Store. Mando ensaje de confirmacion a t1Daemon {event.source_element_id}',
                   "buffer")
        if event.parametros["id_copy"] > 1:
            # Creo clones
            print("Funiona!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!?")
            insert(nodo_info,
                   "T3DaemonID",
                   nodo_info.id,
                   nodo_info.id,
                   event.parametros,
                   "HIGH",
                   "STORE",
                   buffer_id=self.buffer_id,
                   timer=10,
                   source_daemon=event.source_element_id,
                   tipo_daemon="T1DaemonID"
                   )
        else:
            print("Vamos a mandar confirStorage, soy el original", event.parametros["id_copy"])
            add_result(nodo_info, event.parametros['id_copy'],
                       'Vamos a mandar confirmStorage, soy el original', "buffer")
            pass  # Todo: Tengo que escribir lo restante

        resultados = True  # ! Variable de prueba, esto lo deberia de regresar un proceso
        if resultados:
            print(f'Mandamos report cocn buenos resultados {resultados}')
            # todo: this is not a global massage
            add_all(nodo_info, f'Mandamos report con buenos resultados {resultados}', "buffer")
            report_results(nodo_info, resultados)


class QManager:
    def __init__(self):
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
        print("La prioridad es :", event.prioridad)
        elementos = {
            'tipo_daemon': tipo_daemon,
            'nodo_objetivo': event.nodo_objetivo,
            'source': event.source,
            'operacion': event.operacion,
            'parametros': event.parametros
        }
        encolar(self, elementos, event.prioridad)
        print("Deberia encolar!!!!!")
        add_result(nodo_info, event.parametros['id_copy'], "Deberia encolar", "qmanager")

    def retrieve_t1daemon(self):
        pass

    def process_t1daemon(self):
        pass

    def eliminate_copy(self):
        pass

    def free(self, nodo_info, event):
        add_all(nodo_info, '##QManager##')
        #  que puedea hacer
        add_all(nodo_info, f'Se libero el daemon tipo {event.operacion}. ID:{event.target_element_id}')
        print("Se libero el daemon tipo", event.operacion, "Con Id:", event.target_element_id)
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
                        prueba2(self, nodo_info, self.queue_high, free_daemons, "HIGH", id_copy)
                        despachado = True
                    else:  # NO HAY NADA EN LA LISTA DE PRIORIDAD ALTA, CAMBIAMOS POLITICA
                        print("@@No hay nada en la lista de prioirdad alta, cambiamos politica, vamos media")
                        self.politica = "MEDIUM"
                if self.politica == "MEDIUM":
                    print("Entro aca")
                    if self.queue_medium:
                        prueba2(self, nodo_info, self.queue_medium, free_daemons, "MEDIUM", id_copy)
                        despachado = True
                    else:
                        print("@@No hay nada en la lista de prioirdad media, cambiamos politica, vamos baja")
                        self.politica = "LOW"
                if self.politica == "LOW":
                    if self.queue_low:
                        prueba2(self, nodo_info, self.queue_low, free_daemons, "LOW", id_copy)
                        despachado = True
                    else:
                        print("@@No hay nada en la lista de prioirdad baja, cambiamos politica,vamos alta")
                        self.politica = "HIGH"
            else:
                print("No hay tareas pendientes", self.politica)
                print(self.queue_high)
        else:
            print("No hay demonios disponibles")


def prueba2(self, nodo_info, queue, free_daemons, prioridad, id_copy):
    for _ in range(len(queue)):
        tipo_daemon = queue[0]['tipo_daemon']
        if tipo_daemon == 1 and 1 in free_daemons:
            get_free_daemon = freeDaemon(nodo_info.t1_daemons)
            if get_free_daemon != -1:
                print("Se envia trabajo al T1Daemon:", get_free_daemon)
                add_result(nodo_info, id_copy, f'Se envia trabajo al T1Daemon: {get_free_daemon}', "qmanager")
                encargoDaemon(self, nodo_info, prioridad, get_free_daemon, id_copy)
                nodo_info.t1_daemons[get_free_daemon].status = "BUSY"  # Para evitar errores
                # Revisa si hay mas libres aparte de el, cambia a false si no hay
                check_daemons(self, nodo_info, 1)
            else:  # No hay demonios disponibles
                self.status_daemons[0] = False
                print(free_daemons)
                add_result(nodo_info, id_copy, f'{free_daemons}', "qmanager")
                print("Ya no hay demonios T1Daemons")
                add_result(nodo_info, id_copy, "Ya no hay T1Daemons", "qmanager")
                break
        elif tipo_daemon == 2 and 2 in free_daemons:
            get_free_daemon = freeDaemon(nodo_info.t2_daemons)
            if get_free_daemon != -1:
                print("Se envia trabajo al T2Daemon:", get_free_daemon)
                add_result(nodo_info, id_copy, f'Se envia trabajo al T2Daemon: {get_free_daemon}', "qmanager")
                encargoDaemon(self, nodo_info, prioridad, get_free_daemon, id_copy)
                self.t2_daemons[get_free_daemon].status = "BUSY"
                check_daemons(self, nodo_info, 2)
            else:
                self.status_daemons[1] = False
                print("Ya no hay demonios T2Daemons")
                add_result(nodo_info, id_copy, "Ya no hay T2Daemons", "qmanager")
        elif tipo_daemon == 3 and 3:  # in free_daemons:
            # El demonio tipo 3 siempre esta disponible
            # todo: Solo deberia de hacer referencia a un demonio tipo 3
            get_free_daemon = freeDaemon(nodo_info.t3_daemons)  # SOlo hay un demonio tipo 3
            print("Se envia trabajo al T3Daemon:", get_free_daemon)
            add_result(nodo_info, id_copy, f'Se envia trabajo al T3Daemon: {get_free_daemon}', "qmanager")
            encargoDaemon(self, nodo_info, prioridad, get_free_daemon, id_copy)
            # if get_free_daemon != -1:
            #     print("Daemon tipo 3 se le envio el trabajo:", get_free_daemon)
            #     encargoDaemon(self, prioridad, get_free_daemon, tipo_daemon)
            #     self.t3_daemons[get_free_daemon].status = "BUSY"
            #     check_daemons(self, 3)
            # else:
            #     self.status_daemons[2] = False
            #     print("Ya no hay demonios tipo 3")
        # else:
        #     print("Algo malo paso, ver linea 143")
        #     break
        contPrioridad(self, prioridad)


def report_results(self, results):
    print("Reporto los resultados ")
