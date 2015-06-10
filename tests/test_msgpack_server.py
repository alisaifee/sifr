import threading
import unittest
import datetime
import time
import msgpackrpc
from sifr import RPCClient

from sifr.daemon import SifrServer
from sifr.span import Hour, Minute
from sifr.storage import MemoryStorage
from tests import get_free_port


class MsgpackServerTests(unittest.TestCase):
    def setUp(self):
        self.server = None

    def run_server(self):
        self.server.start()

    def test_client_server_full_flow(self):
        storage = MemoryStorage()
        self.server = msgpackrpc.Server(SifrServer(storage))
        port = get_free_port()
        self.server.listen(msgpackrpc.Address('127.0.0.1', port))
        self.server_thread = threading.Thread(target=self.run_server)
        self.server_thread.start()
        time.sleep(0.1)

        cli = RPCClient('127.0.0.1', port)
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
        if self.server:
            self.server.stop()
            self.server_thread.join()

