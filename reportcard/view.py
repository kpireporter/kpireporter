from abc import ABC, abstractmethod

from reportcard.plugin import PluginManager


class ViewException(Exception):
    pass


class View(ABC):

    title = None

    def __init__(self, **kwargs):
        if "title" in kwargs:
            self.title = kwargs.pop("title")
        self._params = kwargs
        self.init()
    
    def get(self, param, default=None) -> any:
        return self._params.get(param, default)

    def init(self):
        pass

    @abstractmethod
    def render(self, datasources, theme=None) -> str:
        pass


class ViewManager(PluginManager):

    namespace = "reportcard.view"
    type_noun = "view"
    exc_class = ViewException

    def render(self, datasource_manager) -> list:
        blocks = []
        for name in self.instances():
            try:
                # TODO: handle theme here somehow
                blocks.append(dict(
                    name=name,
                    title=self.get_instance_attr(name, "title"),
                    output=self.call_instance(name, "render",
                                              datasource_manager)
                ))
            except ViewException as exc:
                self.log.error((
                    f"Error rendering {self.type_noun} {name}: {exc}"))
                blocks.append(dict(
                    title=f"Error rendering {name}",
                    output=None
                ))
        return blocks

