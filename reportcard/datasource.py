from abc import ABC, abstractmethod
import pandas as pd

from reportcard.plugin import PluginManager

import logging
LOG = logging.getLogger(__name__)

EXTENSION_NAMESPACE = 'reportcard.datasource'


class DatasourceError(Exception):
    pass


class Datasource(ABC):

    id = None

    def __init__(self, report, **kwargs):
        self.report = report

        if "id" in kwargs:
            self.id = kwargs.pop("id")

        self.init(**kwargs)

    @abstractmethod
    def init(self, **kwargs):
        pass

    @abstractmethod
    def query(self, input: str) -> pd.DataFrame:
        pass


class DatasourceManager(PluginManager):

    namespace = "reportcard.datasource"
    type_noun = "datasource"
    exc_class = DatasourceError

    def query(self, name, *args, **kwargs) -> pd.DataFrame:
        result = self.call_instance(name, "query", *args, **kwargs)

        if not isinstance(result, pd.core.base.PandasObject):
            raise self.exc_class(
                f"Datasource {name} returned unexpected query result type")

        return result
