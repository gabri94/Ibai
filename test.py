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

    def test10_empty_login(self):
        print "Test Login"
        self._c.connect("127.0.0.1", self.serverport)
        res = self._c.login("", "")
        self._c.disconnect()
        self.assertEqual(res, 0)

    def test11_login(self):
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
        # can't bid for my auction
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

    def test93_close_auction_nowinner(self):
        print "Test Close auction"
        self._c.connect("127.0.0.1", self.serverport)
        self._c.login("gabriel", "pippopippo")
        self._c.sell("libri", "IlPrincipe", 10.5)
        res = self._c.close("libri", "IlPrincipe")
        self._c.disconnect()
        self.assertEqual(res, 8)

    def test94_fail_close_auction(self):
        print "Test Failing Close auction"
        self._c.connect("127.0.0.1", self.serverport)
        self._c.login("gabriel", "pippopippo")
        self._c.bid("libri", "Il Signore degli anelli", 12.5)
        res = self._c.close("libri", "Il Signore degli anelli")
        self._c.disconnect()
        self.assertEqual(res, 7)

    def test991_notif_win(self):
        print "Test Winning Notification"
        c1 = IbaiClient()
        c1.connect("127.0.0.1", 7652)
        c1.login("gabriel", "pippopippo")
        c1.listen_notify(True)
        c1.notify_me()
        c2 = IbaiClient()
        c2.connect("127.0.0.1", 7652)
        c2.login("pippo", "gabrigabri")
        c2.listen_notify(True)
        c2.notify_me()

        c1.sell("libri", "IlPrincipe", 10.5)
        c2.bid("libri", "IlPrincipe", 23)
        c1.close("libri", "IlPrincipe")

        c1.get_notify()
        c2.get_notify()
        #c1.get_notify()
        res = c2.get_notify()['code']

        c1.disconnect()
        c2.disconnect()
        self.assertEqual(res, 2)

    def test992_notif_close_auct(self):
        print "Test Notification when price gets surpassed"
        c1 = IbaiClient()
        c1.connect("127.0.0.1", 7652)
        c1.login("gabriel", "pippopippo")
        c1.listen_notify(True)
        c1.notify_me()
        c2 = IbaiClient()
        c2.connect("127.0.0.1", 7652)
        c2.login("pippo", "gabrigabri")
        c2.listen_notify(True)
        c2.notify_me()

        c1.sell("libri", "IlPrincipino", 10.5)
        c2.bid("libri", "IlPrincipino", 23)
        c1.close("libri", "IlPrincipino")

        res = c2.get_notify()['code']

        c1.disconnect()
        c2.disconnect()

        self.assertEqual(res, 1)

    def test993_notif_manybids(self):
        print "Test Notification when price gets surpassed"
        c1 = IbaiClient()
        c1.connect("127.0.0.1", 7652)
        c1.login("gabriel", "pippopippo")
        c1.listen_notify()
        c1.notify_me()
        c2 = IbaiClient()
        c2.connect("127.0.0.1", 7652)
        c2.login("prova", "prova123prova")
        c2.listen_notify()
        c2.notify_me()
        c3 = IbaiClient()
        c3.connect("127.0.0.1", 7652)
        c3.login("pippo", "gabrigabri")
        c3.listen_notify(print_not=True)
        c3.notify_me()

        c1.sell("libri", "IlGattoConGliStivali", 13.75)
        c2.bid("libri", "IlGattoConGliStivali", 23)
        c3.bid("libri", "IlGattoConGliStivali", 26)
        self.failUnlessEqual(c2.get_notify()['code'], 3)
        c2.bid("libri", "IlGattoConGliStivali", 28)
        self.failUnlessEqual(c3.get_notify()['code'], 3)
        c3.bid("libri", "IlGattoConGliStivali", 30)
        self.failUnlessEqual(c2.get_notify()['code'], 3)

        c1.close("libri", "IlGattoConGliStivali")

        self.assertEqual(c1.get_notify()['code'], 1)
        c1.disconnect()
        c2.disconnect()
        c3.disconnect()


if __name__ == '__main__':
    unittest.main()