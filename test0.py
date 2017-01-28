import unittest
from ibaiclient import IbaiClient


class TestIbai(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestIbai, self).__init__(*args, **kwargs)
        self._c = IbaiClient(True)

    def test_login(self):
        print "Test Login"
        self._c.connect("127.0.0.1", 7652)
        res = self._c.login_json("gabriel", "pippopippo")
        self._c.disconnect()
        self.assertTrue(res)

    def test_wrong_register(self):
        print "Test Wrong Register"
        self._c.connect("127.0.0.1", 7652)
        self._c.login_json("gabriel", "pippopippo")
        res = self._c.register_json("libri")
        self._c.disconnect()
        self.assertFalse(res)

    def test_wrong_register2(self):
        print "Test Wrong Register2"
        self._c.connect("127.0.0.1", 7652)
        self._c.login_json("gabriel", "pippopippo")
        res = self._c.register_json("")
        self._c.disconnect()
        self.assertFalse(res)

    def test_register(self):
        print "Test Register"
        self._c.connect("127.0.0.1", 7652)
        self._c.login_json("gabriel", "pippopippo")
        res = self._c.register_json("elettrodomestici")
        self._c.disconnect()
        self.assertTrue(res)

    def test_sell(self):
        print "Test Sell"
        self._c.connect("127.0.0.1", 7652)
        self._c.login_json("gabriel", "pippopippo")
        res = self._c.sell_json("libri", "goya", str(10))
        self._c.disconnect()
        self.assertTrue(res)

    def test_wrong_sell(self):
        print "Test Wrong Sell"
        self._c.connect("127.0.0.1", 7652)
        self._c.login_json("gabriel", "pippopippo")
        res = self._c.sell_json("libri", "", str(10))
        self._c.disconnect()
        self.assertFalse(res)

    def test_sell_bid(self):
        print "Test Bid"
        self._c.connect("127.0.0.1", 7652)
        self._c.login_json("gabriel", "pippopippo")
        res = self._c.sell_json("libri", "PromessiSposi", str(10))
        res = self._c.bid_json("libri", "PromessiSposi", str(23))
        self._c.disconnect()
        self.assertTrue(res)

    def test_sell_wrongbid(self):
        print "Test Wrong Bid"
        self._c.connect("127.0.0.1", 7652)
        self._c.login_json("gabriel", "pippopippo")
        res = self._c.bid_json("libri", "PromessiSposissimi", str(5))
        self._c.disconnect()
        self.assertFalse(res)


if __name__ == '__main__':
    unittest.main()


'''
t = TestAuctions()
t.connect("127.0.0.1", 7652)
t.login("gabriel", "pippopippo")
t.register("libri")
t.register("elettrodomestici")
t.sell("libri", "goya", str(10))
t.bid("libri", "goya", str(23))
t.bid("vestiti", "Smoking nero usato", str(20))
t.send_cmd(["BAD", "CMD"])
'''
