import unittest
from ibaiclient import IbaiClient


class TestIbai(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestIbai, self).__init__(*args, **kwargs)
        self.serverport = 7652
        self._c = IbaiClient('localhost')

    def test_connection(self):
        print "Test Connection"
        res = self._c.connect("127.0.0.1", self.serverport)
        self.assertTrue(res)

    def test_notify(self):
        print "Test Notify"
        self._c.connect("127.0.0.1", self.serverport)
        print "N1"
        self._c.login("gabriel", "pippopippo")
        print "N2"
        self._c.listen_notify('', 0)
        print "N3"
        res = self._c.notify_me()
        print "N4"
        self._c.stop_notify_worker()
        print "N5"
        self.assertTrue(res)

    def test_login(self):
        print "Test Login"
        self._c.connect("127.0.0.1", self.serverport)
        res = self._c.login("gabriel", "pippopippo")
        self.assertTrue(res)

    def test_wrong_register(self):
        print "Test Wrong Register"
        self._c.connect("127.0.0.1", self.serverport)
        self._c.login("gabriel", "pippopippo")
        res = self._c.register("libri")
        self.assertFalse(res)

    def test_wrong_register2(self):
        print "Test Wrong Register2"
        self._c.connect("127.0.0.1", self.serverport)
        self._c.login("gabriel", "pippopippo")
        res = self._c.register("")
        self.assertFalse(res)

    def test_register(self):
        print "Test Register"
        self._c.connect("127.0.0.1", self.serverport)
        self._c.login("gabriel", "pippopippo")
        res = self._c.register("elettrodomestici")
        self.assertTrue(res)

    def test_sell(self):
        print "Test Sell"
        self._c.connect("127.0.0.1", self.serverport)
        self._c.login("gabriel", "pippopippo")
        res = self._c.sell("libri", "goya", str(10))
        self.assertTrue(res)

    def test_wrong_sell(self):
        print "Test Wrong Sell"
        self._c.connect("127.0.0.1", self.serverport)
        self._c.login("gabriel", "pippopippo")
        res = self._c.sell("libri", "", str(10))
        self.assertFalse(res)

    def test_sell_bid(self):
        print "Test Bid"
        self._c.connect("127.0.0.1", self.serverport)
        self._c.login("gabriel", "pippopippo")
        res = self._c.sell("libri", "PromessiSposi", str(10))
        res = self._c.bid("libri", "PromessiSposi", str(23))
        self.assertTrue(res)

    def test_sell_wrongbid(self):
        print "Test Wrong Bid"
        self._c.connect("127.0.0.1", self.serverport)
        self._c.login("gabriel", "pippopippo")
        res = self._c.bid("libri", "PromessiSposissimi", str(5))
        self.assertFalse(res)


if __name__ == '__main__':
    unittest.main()
