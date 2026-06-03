import random
from abc import ABC, abstractmethod

class EstrategiaPlanta(ABC):
    @abstractmethod
    def escolher(self, duracao):
        pass

class EstrategiaAleatoria(EstrategiaPlanta):
    def escolher(self, duracao):
        return random.choice(["Carvalho", "Cerejeira", "Cacto"])

class EstrategiaPorTempo(EstrategiaPlanta):
    def escolher(self, duracao):
        if duracao >= 3600:
            return "carvalho"
        elif duracao >= 1800:
            return "Cerejeira"
        else:
            return "Cacto"