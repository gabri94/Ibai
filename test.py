import unittest
from ibaiclient import IbaiClient


class TestIbai(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestIbai, self).__init__(*args, **kwargs)
        self.serverport = 7652
        self._c = IbaiClient()

    def test0_connection(self):
        print "Test Connection"
        res = self._c.connect("127.0.0.1", self.serverport)
        self._c.disconnect()
        self.assertTrue(res)

    def test1_login(self):
        print "Test Login"
        self._c.connect("127.0.0.1", self.serverport)
        res = self._c.login("gabriel", "pippopippo")
        self._c.disconnect()
        self.assertEqual(res, 1)

    def test2_notify(self):
        print "Test Notify"
        self._c.connect("127.0.0.1", self.serverport)
        self._c.login("gabriel", "pippopippo")
        self._c.listen_notify()
        res = self._c.notify_me()
        self._c.disconnect()
        self.assertTrue(res)

    def test3_wrong_register(self):
        print "Test Wrong Register"
        self._c.connect("127.0.0.1", self.serverport)
        self._c.login("gabriel", "pippopippo")
        res = self._c.register("libri")
        self._c.disconnect()
        self.assertEqual(res, 0)

    def test4_wrong_register2(self):
        print "Test Wrong Register2"
        self._c.connect("127.0.0.1", self.serverport)
        self._c.login("gabriel", "pippopippo")
        res = self._c.register("")
        self._c.disconnect()
        self.assertEqual(res, 0)

    def test5_register(self):
        print "Test Register"
        self._c.connect("127.0.0.1", self.serverport)
        self._c.login("gabriel", "pippopippo")
        res = self._c.register("elettrodomestici")
        self._c.disconnect()
        self.assertEqual(res, 1)

    def test6_sell(self):
        print "Test Sell"
        self._c.connect("127.0.0.1", self.serverport)
        self._c.login("gabriel", "pippopippo")
        res = self._c.sell("libri", "goya", 10)
        self._c.disconnect()
        self.assertEqual(res, 1)

    def test7_wrong_sell(self):
        print "Test Wrong Sell"
        self._c.connect("127.0.0.1", self.serverport)
        self._c.login("gabriel", "pippopippo")
        res = self._c.sell("libri", "", 10)
        self._c.disconnect()
        self.assertEqual(res, 3)

    def test8_sell_bid(self):
        print "Test Bid"
        self._c.connect("127.0.0.1", self.serverport)
        self._c.login("gabriel", "pippopippo")
        self._c.sell("libri", "PromessiSposi", 10)
        res = self._c.bid("libri", "PromessiSposi", 23)
        #can't bid for my auction
        self._c.disconnect()
        self.assertEqual(res, 5)

    def test9_sell_wrongbid(self):
        print "Test Wrong Bid"
        self._c.connect("127.0.0.1", self.serverport)
        self._c.login("gabriel", "pippopippo")
        res = self._c.bid("libri", "PromessiSposissimi", 5)
        self._c.disconnect()
        self.assertEqual(res, 5)

    def test92_register_unlogged(self):
        print "Test Register w/o login"
        self._c.connect("127.0.0.1", self.serverport)
        res = self._c.register("elettrodomestici")
        self._c.disconnect()
        self.assertEqual(res, 3)

    def test93_close_auction(self):
        print "Test Close auction"
        self._c.connect("127.0.0.1", self.serverport)
        self._c.login("gabriel", "pippopippo")
        self._c.listen_notify()
        self._c.notify_me()
        self._c.sell("libri", "IlPrincipe", 10.5)
        res = self._c.close("libri", "IlPrincipe")
        self._c.notify_me()
        self._c.disconnect()
        self.assertEqual(res, 1)


if __name__ == '__main__':
    unittest.main()
