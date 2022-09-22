import typing
from unittest.mock import MagicMock

import stevedore

if typing.TYPE_CHECKING:
    from kpireport.report import Report


class FakePlugin:
    def __init__(self, report, id=None):
        pass


def make_fake_extension_manager(plugins=[]):
    extensions = [
        stevedore.extension.Extension(
            name, entry_point=MagicMock(), plugin=plugin, obj=None
        )
        for name, plugin in plugins
    ]

    return stevedore.ExtensionManager.make_test_instance(extensions=extensions)


def assert_within_report_range(dateobj, report: "Report"):
    """Check that a given datetime is within the report's start/end range, inclusive."""
    start_of_start = report.start_date.replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    end_of_end = report.end_date.replace(hour=23, minute=59, second=59, microsecond=999)
    assert dateobj >= start_of_start
    assert dateobj <= end_of_end
