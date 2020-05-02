from abc import ABC, abstractmethod
import pandas as pd

from reportcard.plugin import PluginManager

import logging
LOG = logging.getLogger(__name__)

EXTENSION_NAMESPACE = 'reportcard.datasource'


class DatasourceError(Exception):
    """
    A base class for errors originating from the datasource.
    """
    pass


class Datasource(ABC):
    """
    A Datasource is responsible for taking a simple query input string and
    returning a query result in the form of a :class:`pandas.DataFrame`
    instance. One instance of a Datasource may be used by multiple
    :class:`View` instances.

    When the Datasource is initialized, any arguments included in the report
    configuration are passed as keyword arguments to its :meth:`init`
    function. **Note**: this is *not* the same as Python's built-in
    :meth:`__init__`. Each Datasource is required to provide both an
    :meth:`init` function, which is responsible for setting up the Datasource
    with any additional state, and a :meth:`query` function, which provides
    the mechanism to execute a given query and return a
    :class:`pandas.DataFrame` with the results back to the caller.

    The minimum requirement::

        from reportcard.datasource import Datasource

        class MyDatasource(Datasource):
            def init(self, param=None):
                pass

            def query(self, input):
                return pd.DataFrame.empty()

    The above can be referred to like this

    .. code-block:: yaml

        datasources:
          my_datasource:
            plugin: my_datasource
            args:
              param: 1

    :param report: the Report object.
    :type report: :class:`reportcard.Report`
    :param id: the Datasource ID.
    :type id: str
    :param **kwargs: Additional datasource parameters.
    """
    id = None

    def __init__(self, report, **kwargs):
        self.report = report

        if "id" in kwargs:
            self.id = kwargs.pop("id")

        self.init(**kwargs)

    @abstractmethod
    def init(self, **kwargs):
        """Initialize the datasource.

        :param **kwargs: Arbitrary keyword arguments.
        """
        pass

    @abstractmethod
    def query(self, input: str) -> pd.DataFrame:
        """Query the datasource.

        :param str input: Something
        :return: The query result.
        :rtype: pandas.DataFrame
        """
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
