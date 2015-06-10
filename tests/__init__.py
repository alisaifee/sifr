from functools import wraps
import platform
import socket
from nose.plugins.skip import SkipTest

def test_import():
    import sifr

def test_module_version():
    import sifr
    assert sifr.__version__ is not None


def skip_if_pypy(fn):
    @wraps(fn)
    def __inner(*a, **k):
        if platform.python_implementation().lower() == "pypy":
            raise SkipTest
        return fn(*a, **k)
    return __inner

def get_free_port():
    sock = socket.socket()
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port

