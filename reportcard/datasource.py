from abc import ABC, abstractmethod
import pandas as pd

from reportcard.plugin import PluginManager

import logging
LOG = logging.getLogger(__name__)

EXTENSION_NAMESPACE = 'reportcard.datasource'


class DatasourceError(Exception):
    pass


class Datasource(ABC):

    def __init__(self, report, **kwargs):
        self.report = report
        self.init(**kwargs)

    def init(self, **kwargs):
        pass

    @abstractmethod
    def query(self, input: str) -> pd.DataFrame:
        pass


class DatasourceManager(PluginManager):

    namespace = "reportcard.datasource"
    type_noun = "datasource"
    exc_class = DatasourceError

    def plugin_factory(self, plugin_ctor, plugin_kwargs):
        return plugin_ctor(self.report, **plugin_kwargs)

    def query(self, name, *args, **kwargs):
        result = self.call_instance(name, "query", *args, **kwargs)

        if not isinstance(result, pd.DataFrame):
            raise self.exc_class(
                f"Datasource {name} returned unexpected query result type")

        return result
