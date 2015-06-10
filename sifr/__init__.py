"""
"""
import time
from ._version import get_versions

__version__ = get_versions()['version']
del get_versions


class RPCClient(object):
    def __init__(self, host, port, resolutions=None):
        import gsocketpool.pool
        from mprpc import RPCPoolClient

        self.client_pool = gsocketpool.pool.Pool(
            RPCPoolClient,
            dict(host=host, port=port)
        )
        self.resolutions = resolutions or ["year", "month",
                                           "day", "hour", "minute"]

    def incr(self, key, amount=1, resolutions=None):
        with self.client_pool.connection() as client:
            client.call('incr', key, resolutions or self.resolutions, amount)

    def incr_unique(self, key, identity, resolutions=None):
        with self.client_pool.connection() as client:
            client.call(
                'incr_unique', key,
                resolutions or self.resolutions, identity
            )

    def track(self, key, identity, resolutions=None):
        with self.client_pool.connection() as client:
            client.call(
                'track', key,
                resolutions or self.resolutions, identity
            )

    def count(self, key, at, resolution):
        with self.client_pool.connection() as client:
            return client.call(
                'count', key, time.mktime(at.timetuple()), resolution
            )

    def cardinality(self, key, at, resolution):
        with self.client_pool.connection() as client:
            return client.call(
                'cardinality', key, time.mktime(at.timetuple()), resolution
            )

    def uniques(self, key, at, resolution):
        with self.client_pool.connection() as client:
            return set(
                client.call(
                    'uniques', key, time.mktime(at.timetuple()), resolution
                )
            )
