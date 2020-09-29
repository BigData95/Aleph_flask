import copy
import math
import uuid
from back.aleph.config import Config
from back.aleph.auxiliar import invokeOracle
from back.aleph.mensajes import insert, confirmReport, confirmStorage
from back.aleph.memento import ConcreteMemento, Memento
from back.aleph.salidas import add_all, add_result


class Buffer:
    def __init__(self, buffer_id):
        self.__buffer_id = buffer_id
        self.clones_pendientes = list()
        # self.operaciones_pendientes = list()
        self._state = None
        self.files_dispersando = list()
        self.files = list()
        # self.resultados = True # ya me llegaron los resultados? ver store_from_t1daemon

    @property
    def buffer_id(self):
        return self.__buffer_id

    @staticmethod
    def store_from_proxy(nodo_info, event):
        file_, new_name, num_copy = event.parametros
        # informacion = {'file': new_name, 'encargados': list()}
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
            # informacion['encargados'].append(copia, id_nodo)

            print(f"Genera: nodo {nodo_info.id} Nodo generado por oracle: {id_nodo}, con id_copy: {copia}")
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
            confirmReport(nodo_info, event.name, nodo_info.id, "proxy", event.parametros, event.nodo_objetivo)
            # update()  # TODO: Update, actualiza la lista del buffer segun IDFILE e idCopy

    def confirm(self, nodo_info, event):
        add_result(nodo_info, event.parametros['id_copy'], "##Buffer##", "buffer")
        if event.source_element == 't2daemon':
            add_result(nodo_info, event.parametros['id_copy'], "Llego resultado de la dispersion", "buffer")

            # Busco si el id_file esta en los files que estamos esperando.
            index = next((i for i, files in enumerate(self.files_dispersando)
                          if files['id_file'] == event.parametros['id_file']), None)
            if index is not None:
                self.files_dispersando[index]['dispersos_pendientes'] -= 1

                if self.files_dispersando[index]['dispersos_pendientes'] == 0:
                    # Ya se almacenaron todos los dispersos
                    add_result(nodo_info, event.parametros['id_copy'],
                               f"Todos los dispersos de {event.parametros['id_file']} estan almacenados", "buffer")
                    # Deberia de poder matar al clone pero no sabe en que nodo esta programado. Es el nodo que tiene NumCopy=1
                    self.files_dispersando.pop(index)
                    # TODO: deberia de hacer insert a t1daemon, ver instruccion 13 eb Storage Process, second phase
            else:
                print("Whoops")
                # Llego la respuesta a otro nodo, nunca deberia pasar esto

    # @staticmethod
    def store_from_t1daemon(self, nodo_info, event):
        print(f"Nodo: {nodo_info.id}  Buffer clock: {nodo_info.clock} , store desde t1Daemon")
        clone = 0
        add_result(nodo_info, event.parametros['id_copy'], f'##Buffer##', "buffer")
        add_result(nodo_info, event.parametros['id_copy'],
                   f'Tengo que hacer un {event.operacion} a peticion de T1Daemon: {event.source_element_id} del nodo {event.source}',
                   "buffer")

        if event.parametros['id_copy'] == 0:
            add_result(nodo_info, event.parametros['id_copy'],
                       f"Ya esta guardado en el buffer, no hay riesgo de que se pierda.", "buffer")
            # Mas tarde algun t1Daemon te pedira que lo elimines.
            self.files.append(event.parametros['id_file'])
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
            # Creamos el id del clon y guardamos") registro de el para poder eliminarlo despues
            parametros['id_clone'] = uuid.uuid4()
            file_pendiente = {'id_file': parametros['id_file'], 'id_clone': parametros['id_clone']}
            # Solo a quien le toque el NumCopy == 1 hace uso de self.clones_pendientes
            self.clones_pendientes.append(file_pendiente)
            print(
                f"Nodo {nodo_info.id} Creamos clone en buffer {self.clones_pendientes}")
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
        """
        Solo se almacena. Se trata de algun disperso procesado por t2Daemon
        """
        add_result(nodo_info, event.parametros['id_copy'],
                   f"Llego {event.operacion} de algun t2Daemon. Le mando confirmacion", "buffer")
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
                dispersando = {'id_file': event.parametros['id_file'], 'dispersos_pendientes': len(dispersos)}
                self.files_dispersando.append(dispersando)
                print(
                    f"Nodo:{nodo_info.id} Clock {nodo_info.clock} Se crearan {len(dispersos)} T2Daemon por los dipersos, pendientes {self.files_dispersando}")
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