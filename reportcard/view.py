from abc import ABC, abstractmethod
import pandas as pd

from reportcard.plugin import PluginManager


class ViewException(Exception):
    pass


class View(ABC):

    @abstractmethod
    def render(self, theme=None) -> str:
        pass


class ViewManager(PluginManager):

    namespace = "reportcard.view"
    type_noun = "view"
    exc_class = ViewException
