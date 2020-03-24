import pandas as pd
import unittest
from unittest.mock import MagicMock

from reportcard.datasource import DatasourceError
from reportcard.datasource import DatasourceManager
from reportcard.tests.utils import make_test_extension_manager

NAME = "my_datasource"
PLUGIN = "my_plugin"


class DatasourceManagerTestCase(unittest.TestCase):

    def _make_datasource_manager(self, conf={NAME: {"plugin": PLUGIN}},
                                 plugins=[(PLUGIN, MagicMock())]):
        mgr = make_test_extension_manager(plugins)
        return DatasourceManager(conf, extension_manager=mgr)

    def test_invalid_query_return_type(self):
        class TestPlugin():
            def query(self, input):
                return None

        mgr = self._make_datasource_manager(plugins=[(PLUGIN, TestPlugin)])

        with self.assertRaises(DatasourceError):
            mgr.query(NAME, "some input")

    def test_valid_query_result(self):
        df = pd.DataFrame()

        class TestPlugin():
            def query(self, input):
                return df

        mgr = self._make_datasource_manager(plugins=[(PLUGIN, TestPlugin)])

        pd.testing.assert_frame_equal(df, mgr.query(NAME, "some input"))

    def test_multiple_datasources(self):
        df = pd.DataFrame()

        class TestPlugin():
            def query(self, input):
                return df

        mgr = self._make_datasource_manager(
            conf={
                NAME: {"plugin": PLUGIN},
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

        mgr = self._make_datasource_manager(plugins=[
            ("first", FirstTestPlugin),
            (PLUGIN, SecondTestPlugin)
        ])

        pd.testing.assert_frame_equal(df, mgr.query(NAME, "some input"))
