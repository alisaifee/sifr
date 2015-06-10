import unittest
import datetime
from gevent.server import StreamServer
from sifr import RPCClient

from sifr.daemon import SifrServer
from sifr.span import Hour, Minute
from sifr.storage import MemoryStorage
from tests import get_free_port


class MsgpackServerTests(unittest.TestCase):
    def setUp(self):
        self.stream_server = None

    def test_client_server_full_flow(self):
        storage = MemoryStorage()
        server = SifrServer(storage)
        self.stream_server = StreamServer(('127.0.0.1', get_free_port()),
                                          server)
        self.stream_server.start()
        cli = RPCClient('127.0.0.1', self.stream_server.server_port)
        cli.incr("foo", 1)
        self.assertEqual(
            1,
            storage.count(Hour(datetime.datetime.now(), "foo"))
        )
        cli.incr("bar", 1, ["minute"])
        self.assertEqual(
            0,
            storage.count(Hour(datetime.datetime.now(), "bar"))
        )
        self.assertEqual(
            1,
            storage.count(Minute(datetime.datetime.now(), "bar"))
        )
        self.assertEqual(
            1,
            cli.count("foo", datetime.datetime.now(), "hour")
        )
        cli.incr_unique("foo", "test")
        self.assertEqual(
            1,
            storage.cardinality(Hour(datetime.datetime.now(), "foo"))
        )
        self.assertEqual(
            1,
            cli.cardinality("foo", datetime.datetime.now(), "hour")
        )
        cli.track("foo", "test")
        self.assertEqual(
            set(["test"]),
            storage.uniques(Hour(datetime.datetime.now(), "foo"))
        )
        self.assertEqual(
            set(["test"]),
            cli.uniques("foo", datetime.datetime.now(), "hour")
        )

    def tearDown(self):
        if self.stream_server:
            self.stream_server.stop()
