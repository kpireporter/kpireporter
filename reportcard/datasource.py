from abc import ABC, abstractmethod
import pandas as pd
import stevedore

import logging
LOG = logging.getLogger(__name__)

EXTENSION_NAMESPACE = 'reportcard.datasource'


class DatasourceError(Exception):
    pass


class Datasource(ABC):

    @abstractmethod
    def query(self, input: str) -> pd.DataFrame:
        pass


class DatasourceManager:

    @staticmethod
    def _extension_manager_factory():
        def on_load_failure(manager, entrypoint, exception):
            LOG.error(f"Failed to load {entrypoint}: {exception}")

        return stevedore.ExtensionManager(
            namespace=EXTENSION_NAMESPACE,
            invoke_on_load=False,
            on_load_failure_callback=on_load_failure,
        )

    def __init__(self, datasources_config,
                 extension_manager_factory=None):
        if not extension_manager_factory:
            extension_manager_factory = (
                DatasourceManager._extension_manager_factory)

        self._mgr = extension_manager_factory()
        self._datasources = {}

        for name, conf in datasources_config.items():
            try:
                self._datasources[name] = self._init_datasource(name, conf)
                LOG.info(f"Initialized datasource {name}")
            except Exception as exc:
                raise DatasourceError(
                    f"Failed to load datasource {name}") from exc

    def query(self, name, *args, **kwargs):
        result = self._invoke_datasource(name, 'query', *args, **kwargs)

        if not isinstance(result, pd.DataFrame):
            raise DatasourceError(
                f"Datasource {name} returned unexpected query result type")

        return result

    def _invoke_datasource(self, name, method, *args, **kwargs):
        if name not in self._datasources:
            raise DatasourceError(f"Datasource {name} is not loaded")

        plugin = self._datasources[name]
        fn = getattr(plugin, method)

        if not callable(fn):
            raise DatasourceError((
                f"No such method {method} for datasource {name}"))

        return fn(*args, **kwargs)

    def _init_datasource(self, name, config):
        plugin = config.get("plugin")

        if not plugin:
            raise ValueError((
                "Each datasource must define a 'plugin' attribute"))

        if plugin not in self._mgr:
            raise ValueError(f"Plugin {plugin} not loaded")

        plugin_kwargs = config.get("args", {})
        if not isinstance(plugin_kwargs, dict):
            raise ValueError((
                f"Malformed plugin arguments: expected dict, "
                "got {plugin_kwargs}"))

        return self._mgr[plugin].plugin(**plugin_kwargs)
