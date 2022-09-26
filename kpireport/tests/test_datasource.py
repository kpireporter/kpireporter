import pandas as pd
import pytest
from kpireport.datasource import DatasourceError
from kpireport.tests.fixtures import FakePlugin
from kpireport.tests.utils import make_datasource_manager

NAME = "my_datasource"
PLUGIN = "my_plugin"


def test_invalid_query_return_type():
    class TestPlugin(FakePlugin):
        def query(self, input):
            return None

    mgr = make_datasource_manager({NAME: TestPlugin})

    with pytest.raises(DatasourceError):
        mgr.query(NAME, "some input")


def test_valid_query_result():
    df = pd.DataFrame()

    class TestPlugin(FakePlugin):
        def query(self, input):
            return df

    mgr = make_datasource_manager({NAME: TestPlugin})

    pd.testing.assert_frame_equal(df, mgr.query(NAME, "some input"))


def test_multiple_datasources():
    df = pd.DataFrame()

    class TestPlugin(FakePlugin):
        def query(self, input):
            return df

    mgr = make_datasource_manager(
        {
            NAME: TestPlugin,
            "second": TestPlugin,
        }
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

    mgr = make_datasource_manager({"first": FirstTestPlugin, NAME: SecondTestPlugin})

    pd.testing.assert_frame_equal(df, mgr.query(NAME, "some input"))
