import pandas as pd
import pytest
from unittest.mock import MagicMock

from kpireport.datasource import DatasourceError
from kpireport.datasource import DatasourceManager
from kpireport.tests.utils import FakePlugin, make_fake_extension_manager

NAME = "my_datasource"
PLUGIN = "my_plugin"


def make_datasource_manager(conf=None, plugins=None):
    if conf is None:
        conf = {NAME: {"plugin": PLUGIN}}
    if plugins is None:
        plugins = [(PLUGIN, MagicMock())]
    mgr = make_fake_extension_manager(plugins)
    return DatasourceManager(MagicMock(), conf, extension_manager=mgr)


def test_invalid_query_return_type():
    class TestPlugin(FakePlugin):
        def query(self, input):
            return None

    mgr = make_datasource_manager(plugins=[(PLUGIN, TestPlugin)])

    with pytest.raises(DatasourceError):
        mgr.query(NAME, "some input")


def test_valid_query_result():
    df = pd.DataFrame()

    class TestPlugin(FakePlugin):
        def query(self, input):
            return df

    mgr = make_datasource_manager(plugins=[(PLUGIN, TestPlugin)])

    pd.testing.assert_frame_equal(df, mgr.query(NAME, "some input"))


def test_multiple_datasources():
    df = pd.DataFrame()

    class TestPlugin(FakePlugin):
        def query(self, input):
            return df

    mgr = make_datasource_manager(
        conf={
            NAME: {"plugin": PLUGIN},
            "second": {"plugin": PLUGIN},
        },
        plugins=[(PLUGIN, TestPlugin)],
    )

    pd.testing.assert_frame_equal(df, mgr.query("second", "some input"))


def test_multiple_plugins():
    df = pd.DataFrame()

    class FirstTestPlugin(FakePlugin):
        def query(self, input):
            return None

    class SecondTestPlugin(FakePlugin):
        def query(self, input):
            return df

    mgr = make_datasource_manager(
        plugins=[("first", FirstTestPlugin), (PLUGIN, SecondTestPlugin)]
    )

    pd.testing.assert_frame_equal(df, mgr.query(NAME, "some input"))
