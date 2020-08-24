# from abc import ABC, abstractmethod
# from datetime import datetime


# class Memento(ABC):

#     @abstractmethod
#     def get_name(self):
#         pass

#     @abstractmethod
#     def get_date(self):
#         pass


# class ConcreteMemento(Memento):
#     def __init__(self, state):
#         self._state = state
#         self._date = str(datetime.now())[:19]

#     def get_state(self):
#         return self._state

#     def get_name(self):
#         return f'{self._date} / {self._state[0:9]}'

#     def get_date(self):
#         return self._date


# class Caretaker():
#     def __init__(self, originator):
#         self._mementos = []
#         self._originator = originator

#     def save(self):
#         print("Saving Originator's state...")
#         self._mementos.append(self._originator.save())

#     def restore(self):
#         if not len(self._mementos):
#             return
#         memento = self._mementos.pop()
#         print(f'Carataker: Restoring state to: {memento.get_name()}')
#         try:
#             self._originator.restore(memento)
#         except Exception:
#             self.restore()


# class Proxy:
#     def __init__(self):
#         self._state = "Inicio Proxy"

#     @staticmethod
#     def do_something():
#         print("Soy el proxy estoy haciendo algo")


# class Aleph:
#     def __init__(self):
#         self._state = "Inicio"
#         self._nodos = [1, 2, 3, 4]
#         self.proxy = Proxy()
#         self.estoy_vivio = True

#     # @staticmethod
#     def proxy_do(self):
#         self._state = "Hice algo con el proxy"
#         self.proxy.do_something()

#     def save(self):
#         return ConcreteMemento(self._state)

#     def restore(self, memento):
#         self._state = memento.get_state()

#     def ver_estado(self):
#         print(f"Este es mi estado:{self._state}")

#     def check_status(self):
#         return self.estoy_vivio


# class implementacion():
#     def __init__(self):
#         self.algoritmo = Aleph()
#         self.caretaker = Caretaker(self.algoritmo)

#     def recive(self, event):
#         if event == "proxy":
#             if self.algoritmo.check_status():
#                 self.caretaker.save()
#                 self.algoritmo.proxy_do()
#             else:
#                 print("Se ignora el mensaje")

#         if event == "restaurar":
#             self.caretaker.restore()

#     def estado_algoritmo(self):
#         self.algoritmo.ver_estado()



# prueba = implementacion()
# prueba.estado_algoritmo()
# prueba.recive('proxy')
# prueba.estado_algoritmo()
# prueba.recive('restaurar')
# prueba.estado_algoritmo()
