from abc import ABC, abstractmethod
import pandas as pd
import stevedore

from reportcard.plugin import PluginManager

import logging
LOG = logging.getLogger(__name__)

EXTENSION_NAMESPACE = 'reportcard.datasource'


class DatasourceError(Exception):
    pass


class Datasource(ABC):

    @abstractmethod
    def query(self, input: str) -> pd.DataFrame:
        pass


class DatasourceManager(PluginManager):

    namespace = "reportcard.datasource"
    type_noun = "datasource"
    exc_class = DatasourceError

    def query(self, name, *args, **kwargs):
        result = self.call_instance(name, "query", *args, **kwargs)

        if not isinstance(result, pd.DataFrame):
            raise DatasourceError(
                f"Datasource {name} returned unexpected query result type")

        return result
