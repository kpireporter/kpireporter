from abc import ABC, abstractmethod
import pandas as pd

from kpireport.plugin import PluginManager

import logging

LOG = logging.getLogger(__name__)

EXTENSION_NAMESPACE = "kpireport.datasource"


class DatasourceError(Exception):
    """
    A base class for errors originating from the datasource.
    """

    pass


class Datasource(ABC):
    """
    :param report: the Report object.
    :type report: :class:`kpireport.report.Report`
    :param id: the Datasource ID declared in the report configuration.
    :type id: str
    :param **kwargs: Additional datasource parameters, declared as ``args``
                     in the report configuration.
    """

    id = None

    def __init__(self, report, **kwargs):
        self.report = report

        if "id" in kwargs:
            self.id = kwargs.pop("id")

        self.init(**kwargs)

    @abstractmethod
    def init(self, **kwargs):
        """
        Initialize the datasource from the report configuration.

        :param **kwargs: Arbitrary keyword arguments, declared as ``args``
                         in the report configuration.
        """
        pass

    @abstractmethod
    def query(self, input: str) -> pd.DataFrame:
        """
        Query the datasource.

        :param str input: The query string.
        :return: The query result.
        :rtype: pandas.DataFrame
        """
        pass


class DatasourceManager(PluginManager):

    namespace = "kpireport.datasource"
    type_noun = "datasource"
    exc_class = DatasourceError

    def query(self, name, *args, **kwargs) -> pd.DataFrame:
        result = self.call_instance(name, "query", *args, **kwargs)

        if not isinstance(result, pd.core.base.PandasObject):
            raise self.exc_class(
                f"Datasource {name} returned unexpected query result type"
            )

        return result
