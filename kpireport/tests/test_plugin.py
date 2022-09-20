from unittest.mock import MagicMock

from kpireport.plugin import PluginManager
from kpireport.tests.utils import FakePlugin, make_fake_extension_manager

NAME = "my_name"
PLUGIN = "my_plugin"


class FakeException(Exception):
    pass


class FakePluginManager(PluginManager):
    exc_class = FakeException


def make_plugin_manager(conf=None, plugins=None):
    if conf is None:
        conf = {NAME: {"plugin": PLUGIN}}
    if plugins is None:
        plugins = [(PLUGIN, MagicMock())]
    mgr = make_fake_extension_manager(plugins)
    return FakePluginManager(MagicMock(), conf, extension_manager=mgr)


def test_missing_plugin():
    mgr = make_plugin_manager(conf={NAME: {}})
    assert isinstance(mgr.errors(NAME)[0], FakeException)


def test_invalid_plugin():
    mgr = make_plugin_manager(conf={NAME: {"plugin": "missing"}})
    assert isinstance(mgr.errors(NAME)[0], FakeException)


def test_invalid_args():
    mgr = make_plugin_manager(conf={NAME: {"plugin": PLUGIN, "args": "foo"}})
    assert isinstance(mgr.errors(NAME)[0], FakeException)


def test_error_on_invoke():
    def test_plugin():
        raise ValueError("I'm a bad plugin!")

    mgr = make_plugin_manager(plugins=[(PLUGIN, test_plugin)])
    assert isinstance(mgr.errors(NAME)[0], FakeException)


def test_call_instance():
    class TestPlugin(FakePlugin):
        def my_method(self, posarg, kwarg=None):
            return (posarg, kwarg)

    mgr = make_plugin_manager(plugins=[(PLUGIN, TestPlugin)])
    assert mgr.call_instance(NAME, "my_method", 1, kwarg=2) == (1, 2)


def test_multiple_instances():
    class TestPlugin(FakePlugin):
        def my_method(self, posarg):
            return posarg

    mgr = make_plugin_manager(
        conf={
            "first": {"plugin": PLUGIN},
            "second": {"plugin": PLUGIN},
        },
        plugins=[(PLUGIN, TestPlugin)],
    )

    assert mgr.call_instance("second", "my_method", "arg") == "arg"


def test_multiple_plugins():
    class FirstTestPlugin(FakePlugin):
        def my_method(self, input):
            return None

    class SecondTestPlugin(FakePlugin):
        def my_method(self, input):
            return input

    mgr = make_plugin_manager(
        plugins=[("first", FirstTestPlugin), (PLUGIN, SecondTestPlugin)]
    )

    assert mgr.call_instance(NAME, "my_method", "arg") == "arg"
