import os
import tempfile

import pytest
from cryptography.fernet import Fernet

# Declare any shared fixtures from the base package here
from kpireport.tests.fixtures import report


@pytest.fixture(scope="package")
def google_oauth2_keyfile():
    encfile_name = "test_google_oauth2_key.json.enc"
    with open(os.path.join(os.path.dirname(__file__), encfile_name), "r") as encfile:
        key = os.getenv("KPIREPORT_ENCRYPTION_KEY")
        decrypted = Fernet(key).decrypt(encfile.read())
        with tempfile.NamedTemporaryFile("wb") as f:
            f.write(decrypted)
            f.flush()
            yield f.name
