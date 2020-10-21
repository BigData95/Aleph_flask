from back.aleph.config import Config
from back.aleph.salidas import add_all, add_result
from back.aleph.mensajes import store, confirmReport, informacion_proxy, kill_clone
from back.aleph.auxiliar import generateNewName
from back.aleph.memento import ConcreteMemento, Memento


class Proxy:
    def __init__(self):
        self._state = None
        # Cada que llega guarda el id_file y el nodo_id, sin importar si ya se guardo antes en algun copy
        self.record = {'id_file': [], 'nodo_id': []}
        # Aqui solo hay un unico id_file
        self.cont_copies = {'id_file': [], 'copies_store': []}
        self.despachados = []

    @staticmethod
    def store(nodo_info, event):
        add_all(nodo_info, "##Proxy", "proxy")
        add_all(nodo_info, 'Genero nombre archivo', "proxy")
        file_, file_name = event.parametros
        new_name = generateNewName(file_name)
        parametros = [file_, new_name, Config.NUM_COPIES]  # FileID es NewName
        store(nodo_info, parametros, nodo_info.id, event.extras)  # Para buffer

    def confirm(self, nodo_info, event):
        # EL resultado viene en event.operacion
        add_result(nodo_info, event.parametros['id_copy'], "##Proxy##", "proxy")
        add_result(nodo_info, event.parametros['id_copy'], "LLego confirmacion. Hago update", "proxy")
        if event.operacion == "SUCESS":
            # Buscamos si ya teniamos registro del id_file anteriormente
            for file in self.cont_copies['id_file']:
                if file == event.parametros['id_file']:
                    # No es el primer copy que llega. Se aumenta el cotador
                    index = self.cont_copies['id_file'].index(file)
                    self.cont_copies['copies_store'][index] += 1
                    if self.cont_copies['copies_store'][index] >= Config.CONFIRM_COPIES:
                        add_result(nodo_info, event.parametros['id_copy'], "Mando confirmacion al cliente.", 'proxy')
                        confirmReport(nodo_info, "SUCESS", nodo_info.id, "cliente", event.parametros)
                    break
            else:
                self.cont_copies['id_file'].append(event.parametros['id_file'])
                self.cont_copies['copies_store'].append(1)
                # Realmente entra a este if solo si Config.CONFIRM_COPIES es igual a cero.
                if self.cont_copies['copies_store'][-1] >= Config.CONFIRM_COPIES:
                    add_result(nodo_info, event.parametros['id_copy'], "Mando confirmacion al cliente.", 'proxy')
                    confirmReport(nodo_info, "SUCESS", nodo_info.id, "cliente", event.parametros)
            self.record['id_file'].append(event.parametros['id_file'])
            self.record['nodo_id'].append(event.nodo_objetivo)

    def info(self, nodo_info, event):
        self.update_despachados(event.parametros)
        if event.source_element is "buffer":
            for proxy in range(Config.NODO_PROXY_LOWER, Config.NODO_PROXY_UPPER + 1):
                if proxy is not nodo_info.id:
                    informacion_proxy(nodo_info, proxy, event.parametros, "proxy")
        print(f"Id {nodo_info.id} {self.despachados}")

    def update_despachados(self, parametros):
        for elemento in self.despachados:
            if parametros['id_file'] in elemento.values():
                elemento.update(parametros)
                break
        else:
            self.despachados.append(parametros)

    def matar_clon(self, nodo_info, event):
        for elemento in self.despachados:
            if event.parametros['id_file'] in elemento.values():
                try:
                    target = elemento['nodos_con_copias'][-1]
                    kill_clone(nodo_info,
                               target,
                               {
                                   'id_copy': 2,
                                   'id_clone': elemento['id_clone']
                               },
                               "proxy",
                               nodo_info.id)
                except KeyError:
                    print("Esto no deberia pasar compa")
                    print(event.parametros)
                print(f"Mato algo {self.despachados}")



    # def retrive():
    #     pass

    def save(self) -> ConcreteMemento:
        # todo: Cuando se modifica el estado?
        self._state = "State de Proxy"
        return ConcreteMemento(self._state)

    def restore(self, memento: Memento):
        self._state = memento.get_state()
        # todo: Igualar todos las propiedades necesarias
