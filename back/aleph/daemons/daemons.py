from back.aleph.memento import ConcreteMemento, Caretaker, Memento


"""

"""


class Daemon:
    def __init__(self, daemon_id, status="FREE"):
        self._state = None
        self.__daemon_id = daemon_id
        self.__status_daemon = status

    @property
    def daemon_id(self):
        return self.__daemon_id

    @property
    def status(self):
        return self.__status_daemon

    @status.setter
    def status(self, new_status):
        self.__status_daemon = new_status

    def save(self) -> ConcreteMemento:
        # todo: Cuando se modifica el estado?
        self._state = 'state de daemon'
        return ConcreteMemento(self._state)

    def restore(self, memento: Memento):
        self._state = memento.get_state()
        # todo: Igualar todos las propiedades necesarias

#
# class T2Daemon(Daemon):
#     def __init__(self, __daemon_id, __status="FREE"):
#         super().__init__(__daemon_id, __status)
#         self._state = None
#         self.results = list()
#         self.clones_pendientes = list()
#         self.id_operacion = 0
#
#     def execute(self, nodo_info, event):
#         add_result(nodo_info, event.parametros['id_copy'],
#                    f'Execute desde T2Daemon {event.target_element_id}', "t2daemon")
#         self.status = "BUSY"
#         # invokeOracle() le regresa el estado del nodo segun el HBManager, aqui supondremos que siempre lo manda
#         parametros = copy.copy(event.parametros)
#         if parametros['taskReplica'] == 0:
#             # Solo entra aqui la primera vez
#             parametros['taskReplica'] = 1
#             parametros['id_operacion_t2daemon'] = self.id_operacion
#             self.id_operacion += 1
#             self.results.append(False)
#             add_result(nodo_info, event.parametros['id_copy'], f"Creamos clon", "t2daemon")
#             parametros['id_clone'] = uuid.uuid4()
#             self.clones_pendientes.append(parametros['id_clone'])
#             insert(nodo_info,
#                    "T3DaemonID",
#                    nodo_info.id,
#                    nodo_info.id,
#                    parametros,
#                    event.prioridad,
#                    event.operacion,
#                    elemento_interno_remitente="t3daemon",
#                    daemon_id=self.daemon_id,
#                    nodo_objetivo=event.nodo_objetivo,
#                    timer=Config.CLONE_TIMER,
#                    charge_daemon="t2daemon",
#                    )
#             confirmStorage(nodo_info,
#                            event.operacion,
#                            nodo_info.id,
#                            "buffer",
#                            parametros,
#                            event.nodo_objetivo,
#                            remitente_interno="t2daemon",
#                            remitente_interno_id=self.daemon_id)
#         if parametros['id_clone'] in self.clones_pendientes:
#             invokeTask(nodo_info,
#                        event.nodo_objetivo,
#                        "STORE_DISPERSO",
#                        parametros,
#                        self.daemon_id,
#                        "t2daemon")
#             startTimer(nodo_info,
#                        parametros,
#                        event.operacion,
#                        self.daemon_id,
#                        event.nodo_objetivo,
#                        event.prioridad,
#                        "t2daemon")
#         else:
#             add_result(nodo_info, event.parametros['id_copy'], f"No se hace insert, ya se habia eliminado el clon",
#                        "t2daemon")
#             # Ya se habia eliminado el clon segun t2daemon pero el t3daemon no sabia
#             kill_clone(nodo_info, parametros, "t2daemon", self.daemon_id)
#             self.status = "FREE"
#             mensajeDaemon(nodo_info, "FREE", self.daemon_id, "t2daemon", "2", event.parametros['id_copy'])
#
#     def timer(self, nodo_info, event):
#         # add_result(nodo_info, event.parametros['id_copy'], "Timer T2 Daemon, se hace insert", "t2daemon")
#         # LLego resultado
#         # TODO: Esto esta al reves
#         if self.results[event.parametros['id_operacion_t2daemon']]:
#             add_result(nodo_info, event.parametros['id_copy'],
#                        f"Timer: LLego la respuesta antes de expirar el timer, el clon ya se elimino. No hago insert",
#                        "t2daemon")
#         else:
#             add_result(nodo_info, event.parametros['id_copy'],
#                        f"Timer: No ha llegado la respuesta {event.operacion},hago insert", "t2daemon")
#             event.parametros['taskReplica'] += 1
#             insert(nodo_info,
#                    "T2DaemonID",
#                    nodo_info.id,
#                    nodo_info.id,
#                    event.parametros,
#                    event.prioridad,
#                    event.operacion,
#                    elemento_interno_remitente="t2daemon",
#                    nodo_objetivo=event.nodo_objetivo,
#                    daemon_id=self.daemon_id
#                    )
#         self.status = "FREE"
#         mensajeDaemon(nodo_info, "FREE", self.daemon_id, "t2daemon", "2", event.parametros['id_copy'])
#
#     def confirm(self, nodo_info, event):
#         if self.results[event.parametros['id_operacion_t2daemon']]:
#             add_result(nodo_info, event.parametros['id_copy'],
#                        f"Ya se habia confirmado esta la operacion {event.operacion}")
#         else:
#             add_result(nodo_info, event.parametros['id_copy'],
#                        f"LLega confirmacion de operacion. Tengo que mata al clon: {event.parametros['id_clone']}",
#                        "t2daemon")
#             self.results[event.parametros['id_operacion_t2daemon']] = True
#             parametros = {'id_clone': event.parametros['id_clone'], 'id_copy': event.parametros['id_copy']}
#             kill_clone(nodo_info, parametros, "t2daemon", self.daemon_id)
#             try:
#                 self.clones_pendientes.remove(event.parametros['id_clone'])
#             except ValueError:
#                 print(f"Nodo:{nodo_info.id}. T2Daemon: {self.daemon_id}.Alguien mas habia elimnado este clon")
#
#     def save(self) -> ConcreteMemento:
#         # todo: Cuando se modifica el estado?
#         self._state = 'state de daemon'
#         return ConcreteMemento(self._state)
#
#     def restore(self, memento: Memento):
#         self._state = memento.get_state()
#         # todo: Igualar todos las propiedades necesarias
#
#
# class T3Daemon(Daemon):
#     def __init__(self, __daemon_id, __status='FREE'):
#         super().__init__(__daemon_id)
#         self._state = None
#         self.__clones = list()
#         self.__matar_clon = list()
#         # self.__parametros = None
#
#     def execute(self, nodo_info, event):
#         parametros = copy.copy(event.parametros)
#         add_result(nodo_info, parametros['id_copy'], "Execute Daemon 3, inicio timer", "t3daemon")
#         # Create clone, ya debe de venir dentro de los parametros
#         self.__clones.append(event.parametros['id_clone'])
#         parametros['prioridad'] = event.prioridad
#         parametros['nodo_objetivo'] = event.nodo_objetivo
#         parametros['source_id'] = event.source_element_id
#         startTimerClone(nodo_info,
#                         event.parametros['timer'],
#                         event.operacion,
#                         parametros,
#                         self.daemon_id
#                         )
#
#     def timer(self, nodo_info, event):
#         add_result(nodo_info, event.parametros['id_copy'], "Timer de T3Daemon", "t3daemon")
#         if event.parametros['id_clone'] in self.__clones:
#             add_result(nodo_info, event.parametros['id_copy'], "Mando insert", "t3daemon")
#             if event.parametros['charge_daemon'] == "t1daemon":
#                 daemon = "T1DaemonID"
#             else:  # if event.parametros['charge_daemon'] == "T2DaemonID":
#                 daemon = "T2DaemonID"
#             insert(nodo_info,
#                    daemon,  # event.parametros['charge_daemon'],
#                    nodo_info.id,
#                    nodo_info.id,
#                    event.parametros,
#                    event.parametros['prioridad'],
#                    event.operacion,
#                    elemento_interno_remitente="t3Daemon",
#                    nodo_objetivo=event.parametros['nodo_objetivo'],
#                    daemon_id=event.parametros['source_id']
#                    )
#         else:
#             add_result(nodo_info, event.parametros['id_copy'], "Este clon ya se mato, no se hace insert", "t3daemon")
#
#     def kill(self, nodo_info, event):
#         if event.parametros['id_clone'] in self.__clones:
#             add_result(nodo_info, event.parametros['id_copy'],
#                        f"Kill: LLega mensaje para eliminar clon{event.parametros['id_clone']}, lo eliminamos", "t3daemon")
#             self.__clones.remove(event.parametros['id_clone'])
#         else:
#             pass
#             # print(f"Clock:{nodo_info.clock}, KILL. No esta el clon {event.parametros['id_clone']}, esta en otro nodo o ya se elimino")
#
#     def save(self) -> ConcreteMemento:
#         # todo: Cuando se modifica el estado?
#         self._state = 'state de daemon'
#         return ConcreteMemento(self._state)
#
#     def restore(self, memento: Memento):
#         self._state = memento.get_state()
#         # todo: Igualar todos las propiedades necesarias
