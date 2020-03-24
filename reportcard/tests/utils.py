import stevedore
from unittest.mock import MagicMock


def make_test_extension_manager(plugins=[]):
    extensions = [
        stevedore.extension.Extension(
            name, entry_point=MagicMock(), plugin=plugin, obj=None)
        for name, plugin in plugins]

    return stevedore.ExtensionManager.make_test_instance(
        extensions=extensions
    )
