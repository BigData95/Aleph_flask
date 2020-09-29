from back.aleph.config import Config
from back.aleph.salidas import add_all, add_result
from back.aleph.mensajes import store, confirmReport
from back.aleph.auxiliar import generateNewName
from back.aleph.memento import ConcreteMemento, Memento


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
