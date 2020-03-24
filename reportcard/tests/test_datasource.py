from functools import partial
import pandas as pd
import stevedore
import unittest
from unittest.mock import MagicMock

from reportcard.datasource import DatasourceError
from reportcard.datasource import DatasourceManager

DATASOURCE = "my_datasource"
PLUGIN = "my_plugin"


class TestDatasource(unittest.TestCase):

    def setUp(self):
        def extension_manager_factory(plugins=[(PLUGIN, MagicMock())]):
            extensions = [
                stevedore.extension.Extension(
                    name, entry_point=MagicMock(), plugin=plugin, obj=None)
                for name, plugin in plugins]

            return stevedore.ExtensionManager.make_test_instance(
                extensions=extensions
            )

        self.extension_manager_factory = extension_manager_factory

    def test_missing_plugin(self):
        with self.assertRaises(DatasourceError):
            DatasourceManager({DATASOURCE: {}})

    def _make_datasource_with_plugins(self, plugins=None,
                                      conf={DATASOURCE: {"plugin": PLUGIN}}):
        factory = partial(self.extension_manager_factory,
                          plugins=plugins)
        return DatasourceManager(conf, extension_manager_factory=factory)

    def test_invalid_plugin(self):
        with self.assertRaises(DatasourceError):
            DatasourceManager(
                {DATASOURCE: {"plugin": "missing"}},
            )

    def test_invalid_args(self):
        with self.assertRaises(DatasourceError):
            DatasourceManager(
                {DATASOURCE: {"plugin": PLUGIN, "args": "foo"}},
                extension_manager_factory=self.extension_manager_factory
            )

    def test_raises_on_invoke(self):
        def test_plugin():
            raise ValueError("I'm a bad plugin!")

        with self.assertRaises(DatasourceError):
            self._make_datasource_with_plugins([(PLUGIN, test_plugin)])

    def test_invalid_query_return_type(self):
        class TestPlugin():
            def query(self, input):
                return None

        mgr = self._make_datasource_with_plugins([(PLUGIN, TestPlugin)])

        with self.assertRaises(DatasourceError):
            mgr.query(DATASOURCE, "some input")

    def test_valid_query_result(self):
        df = pd.DataFrame()

        class TestPlugin():
            def query(self, input):
                return df

        mgr = self._make_datasource_with_plugins([(PLUGIN, TestPlugin)])

        pd.testing.assert_frame_equal(df, mgr.query(DATASOURCE, "some input"))

    def test_multiple_datasources(self):
        df = pd.DataFrame()

        class TestPlugin():
            def query(self, input):
                return df

        mgr = self._make_datasource_with_plugins(
            conf={
                DATASOURCE: {"plugin": PLUGIN},
                "second": {"plugin": PLUGIN},
            },
            plugins=[(PLUGIN, TestPlugin)])

        pd.testing.assert_frame_equal(df, mgr.query("second", "some input"))

    def test_multiple_plugins(self):
        df = pd.DataFrame()

        class FirstTestPlugin():
            def query(self, input):
                return None

        class SecondTestPlugin():
            def query(self, input):
                return df

        mgr = self._make_datasource_with_plugins([
            ("first", FirstTestPlugin),
            (PLUGIN, SecondTestPlugin)
        ])

        pd.testing.assert_frame_equal(df, mgr.query(DATASOURCE, "some input"))
