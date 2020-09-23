from abc import ABC, abstractmethod
from datetime import datetime


class Memento(ABC):

    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def get_date(self):
        pass


class ConcreteMemento(Memento):
    def __init__(self, state):
        self._state = state
        self._date = str(datetime.now())[:19]

    def get_state(self):
        return self._state

    def get_name(self):
        return f'{self._date}'  # / {self._state[0:9]}'

    def get_date(self):
        return self._date


class Caretaker:
    def __init__(self, originator):
        self._mementos = []
        self._originator = originator

    def save(self):
        print("Saving Originator's state...")
        self._mementos.append(self._originator.save())

    def restore(self):
        if not len(self._mementos):
            return
        memento = self._mementos.pop()
        print(f'Carataker: Restoring state to: {memento.get_name()}')
        try:
            self._originator.restore(memento)
        except Exception:
            self.restore()


class Proxy:
    def __init__(self):
        self._state = "Inicio Proxy"

    @staticmethod
    def do_something():
        print("Soy el proxy estoy haciendo algo")


class Aleph:
    def __init__(self):
        self.status = None
        self.estoy_activo = True
        self._nodos = [1, 2, 3, 4]
        self.proxy = Proxy()
        self.politica = "HIGH"

    # @staticmethod
    def proxy_do(self):
        self.estoy_activo = False
        self.politica = "WTF"
        self.proxy.do_something()

    def save(self):
        self.status = {
            'politica': self.politica,
            'en_fallo': self.estoy_activo
        }
        print(f"Esto es lo que voy a guardar:{self.status}")
        return ConcreteMemento({
            'politica': self.politica,
            'en_fallo': self.estoy_activo
        })

    def restore(self, memento):
        self.status = memento.get_state()
        self.politica = self.status['politica']
        self.estoy_activo = self.status['en_fallo']

    def ver_estado(self):
        print(f"Este es mi estado Guardado{self.status}")
        print(f"Politica {self.politica} Fallo {self.estoy_activo}")

    def caido(self):
        return self.estoy_activo


class implementacion:
    def __init__(self):
        self.algoritmo = Aleph()
        self.caretaker = Caretaker(self.algoritmo)
        self.parametro = 0
        self.snap = None

    def recive(self, event):
        if event == "proxy":
            if self.algoritmo.caido():
                self.snapshot()
                # self.caretaker.save()
                self.algoritmo.proxy_do()
                self.parametro += 1
            else:
                print("Se ignora el mensaje")

        if event == "restaurar":
            self.restaura()
            # self.caretaker.restore()

    def estado_algoritmo(self):
        self.algoritmo.ver_estado()
        print(f"Diccionario: {self.snap}")

    def snapshot(self):
        print("Tomando snapShot")
        self.caretaker.save()
        self.snap = {'parametros': self.parametro}

    def restaura(self):
        self.caretaker.restore()


prueba = implementacion()
print()
prueba.estado_algoritmo()
prueba.recive('proxy')
print()
prueba.estado_algoritmo()
print()
prueba.recive('restaurar')
prueba.estado_algoritmo()
