from abc import ABC, abstractmethod

class ToolBoxPage(ABC):
    @abstractmethod
    def gui(self):
        pass