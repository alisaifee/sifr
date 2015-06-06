import platform
import sys


class CHLL(object):
    def __init__(self):
        from HLL import HyperLogLog

        self.hll = HyperLogLog(16)

    def add(self, identity):
        self.hll.add(str(identity))

    def count(self):
        return int(self.hll.cardinality())

class HLL(object):
    def __init__(self):
        from hyperloglog import HyperLogLog

        self.hll = HyperLogLog(0.005)

    def add(self, identity):
        self.hll.add(str(identity))

    def count(self):
        return int(self.hll.card())


def get_hll():
    if platform.python_implementation().lower() == "pypy":
        return HLL
    else:
        return CHLL
