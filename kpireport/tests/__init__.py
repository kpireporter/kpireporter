import pytest

# Register the utils module so that assertion helpers are rewritten by pytest
# in order to get better output. This is in __init__ rather than conftest so that
# tests outside of this hierachy can import the utils module and have it be
# autoregistered; conftest only runs when executing a test w/in this dir structure.
pytest.register_assert_rewrite("kpireport.tests.utils")
