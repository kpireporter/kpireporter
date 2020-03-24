from functools import partial
import pandas as pd
import stevedore
import unittest
from unittest.mock import MagicMock

from reportcard.datasource import DatasourceError, DatasourceLoadError
from reportcard.datasource import DatasourceManager

DATASOURCE = "my_datasource"
PLUGIN = "my_plugin"


class TestDatasource(unittest.TestCase):

    def setUp(self):
        def extension_manager_factory(plugin=MagicMock()):
            test_ext = stevedore.extension.Extension(
                PLUGIN, entry_point=MagicMock(), plugin=plugin, obj=None)

            return stevedore.ExtensionManager.make_test_instance(
                extensions=[test_ext]
            )

        self.extension_manager_factory = extension_manager_factory

    def test_missing_plugin(self):
        with self.assertRaises(DatasourceLoadError):
            DatasourceManager({DATASOURCE: {}})

    def test_invalid_plugin(self):
        with self.assertRaises(DatasourceLoadError):
            DatasourceManager({DATASOURCE: {"plugin": PLUGIN}})

    def test_invalid_args(self):
        with self.assertRaises(DatasourceLoadError):
            DatasourceManager(
                {DATASOURCE: {"plugin": PLUGIN, "args": "foo"}},
                extension_manager_factory=self.extension_manager_factory
            )

    def _make_datasource_with_plugin(self, plugin):
        factory = partial(self.extension_manager_factory,
                          plugin=plugin)
        return DatasourceManager(
            {DATASOURCE: {"plugin": PLUGIN}},
            extension_manager_factory=factory
        )

    def test_raises_on_invoke(self):
        def test_plugin():
            raise ValueError("I'm a bad plugin!")

        with self.assertRaises(DatasourceLoadError):
            self._make_datasource_with_plugin(test_plugin)

    def test_invalid_query_return_type(self):
        class TestPlugin():
            def query(self, input):
                return None

        mgr = self._make_datasource_with_plugin(TestPlugin)

        with self.assertRaises(DatasourceError):
            mgr.query(DATASOURCE, "some input")

    def test_valid_query_result(self):
        df = pd.DataFrame()

        class TestPlugin():
            def query(self, input):
                return df

        mgr = self._make_datasource_with_plugin(TestPlugin)

        pd.testing.assert_frame_equal(df, mgr.query(DATASOURCE, "some input"))
