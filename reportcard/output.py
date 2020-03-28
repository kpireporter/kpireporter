from abc import ABC, abstractmethod

from reportcard.plugin import PluginManager


class OutputDriverError(Exception):
    pass


class OutputDriver(ABC):
    id: str = None

    def __init__(self, report, **kwargs):
        self.report = report
        if "id" in kwargs:
            self.id = kwargs.pop("id")
        self.init(**kwargs)

    @abstractmethod
    def init(self, **kwargs):
        pass

    def render_blob_inline(self, blob):
        raise NotImplementedError("This driver does not support inline blobs")

    @abstractmethod
    def render_output(self, content, blobs):
        pass


class OutputDriverManager(PluginManager):
    namespace = "reportcard.output"
    type_noun = "output driver"
    exc_class = OutputDriverError