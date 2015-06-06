from hyperloglog import HyperLogLog


class HLL(object):
    def __init__(self):
        self.hll = HyperLogLog(0.005)

    def add(self, identity):
        self.hll.add(str(identity))

    def count(self):
        return int(self.hll.card())
