import hmac
import json
import socket
import threading
import time

from model.category import Category
from model.ibai_exceptions import *
from model.auction import Auction

from utils import error_print, debug_print


def synchronized(l):
    """Synchronizer decorator
    :param l: lock variable
    :return: function decorated with lock
    """
    def wrap(funct):
        def LockedFunction(*args, **kw):
            l.acquire()
            try:
                return funct(*args, **kw)
            finally:
                l.release()
        return LockedFunction
    return wrap

myLock = threading.Lock()


class ClientManager(threading.Thread):
    """
    This class manage the communication with the single client
    """

    def __init__(self, cs, address, auct):
        """Initalize the Client Manager
        :param cs: client socket
        :param address: remote address
        :param auct: reference to the auction object
        """
        threading.Thread.__init__(self)
        self._address = address
        self._cs = cs
        self._auct = auct
        self.logged = False
        self.user = None
        self.go = True

    def run(self):
        """Main loop of the Thread, here listens for the client msgs
        :return: return when the connnection closes
        """
        while(self.go):
            try:
                msg = self._cs.recv(1024)
            except socket.error:
                return
            if msg == "":
                self.go = False
            else:
                msgs = msg.split('\r\n')
                msgs.pop()  # remove last msg
                for l in msgs:
                    self.read_command(l)
        self._cs.close()

    def read_command(self, line):
        """Read a message received by socket and perform the right command
        :param line: line read on the socket
        :return: return when it has been executed
        """
        json_d = json.loads(line)
        if json_d['msg_id'] == 11:  # Login
            self.login(json_d['user'], json_d['pass'])
            return
        if json_d['msg_id'] == 12:  # Logout
            self.go = False
            return
        if not self.check_session(json_d):
            # invalid session
            return
        if json_d['msg_id'] == 31:  # Register category
            self.register(json_d['category'])
            return
        if json_d['msg_id'] == 41:  # Register auction
            self.sell(json_d['category'], json_d['product'], json_d['price'])
            return
        if json_d['msg_id'] == 51:  # Make a bid
            self.buy(json_d['category'], json_d['product'], json_d['price'])
            return
        if json_d['msg_id'] == 52:  # Remove last bid
            self.unbuy(json_d['category'], json_d['product'])
            return
        if json_d['msg_id'] == 53:  # Remove last bid
            self.close_bid(json_d['category'], json_d['product'])
            return
        if json_d['msg_id'] == 21:  # Register the endpoint for push notif
            self.user.update_notif_socket(json_d['host'], json_d['port'])
            try:
                self.user.notify(1, "Notifiche attivate")
                self.response(1, "Notifiche ok")
            except Exception, e:
                self.response(0, "Erorre connessione notifiche")
            return
        self.response(-1, "Comando non valido")
        return

    def check_session(self, session):
        if 'token' not in session.keys() or not session['token']:
            self.response(3, "Errore, sessione invalida")
            return False
        session = session['token']

        # check if the session is expired
        if(int(session['expire']) - time.time() < 0):
            self.response(2, "Errore, sessione scaduta")
            return False
        server_mac = hmac.new(self._auct._key)
        server_mac.update(session['username'])
        server_mac.update(session['expire'])
        # check if the session token is valid
        if(hmac.compare_digest(server_mac.hexdigest(), str(session['token']))):
            return True
        else:
            self.response(3, "Errore, sessione non valida")
            print "UNAUTHORIZED"
            return False

    def gen_session(self):
        """Generate the session tocken for the logged user
        :return: json session token
        """
        now = time.time()
        # add 24h to the current time 60*60*24
        expire = str(int(now + 86400))
        mac = hmac.new(self._auct._key)
        mac.update(self.user.name)
        mac.update(expire)
        session = {"username": self.user.name, "expire": expire, "token": mac.hexdigest()}
        return session

    def login(self, user, pwd):
        """
        Log a user on the server
        :param user: username
        :param pwd: MD5 hash of the password
        """
        username = user
        try:
            self.user = self._auct._users[username]
            token = ""
            if self.user.password == pwd:
                # Login effettuato
                self.logged = True
                self.response(1, token=self.gen_session())
                return
            debug_print("Password non valida")
            self.response(0, "Password non valida", token="")
        except KeyError, e:
            error_print("Utente non trovato")
            self.response(0, "Utente non trovato", token="")

    @synchronized(myLock)
    def register(self, cat_name):
        """Register a new category
        :param cat_name: category name
        """
        if not cat_name:
            self.response(0, res_msg="Invalid category name")
            return
        if cat_name in self._auct._categories:
            self.response(0, res_msg="Categoria gia' esistente")
            return
        try:
            self._auct._categories[cat_name] = Category(cat_name)
        except Exception, e:
            self.response(0, "Categoria non valida")
        finally:
            self.response(1)

    @synchronized(myLock)
    def sell(self, cat_name, prod_name, price):
        """ Add a new product on the server
        :param cat_name: category name
        :param prod_name: product name
        :param price: base price for the auction
        """
        print "Selling: "
        print price
        try:
            cat = Category.search_category(self._auct._categories, cat_name)
            a = Auction(prod_name, price, self.user)
            cat.add_auction(a)
            self.response(1)
        except CategoryException, e:
            debug_print(e)
            self.response(0, res_msg=str(e))
        except AuctionException, e:
            self.response(3, res_msg=str(e))

    @synchronized(myLock)
    def buy(self, cat_name, prod_name, price):
        """ Place a bid on a product
        :param cat_name: category name
        :param prod_name: product name
        :param price: value of the bid
        """
        try:
            cat = Category.search_category(self._auct._categories, cat_name)
            auct = cat.search_auction(prod_name)
            auct.bid(price=price, user=self.user)
            self.response(1)
        except UserException, e:
            self.response(5, res_msg=str(e))
        except CategoryException, e:
            debug_print(e)
            self.response(4, res_msg="Category not found")
        except ExistingAuctionException, e:
            self.response(5, res_msg="Auction not found")

    @synchronized(myLock)
    def unbuy(self, cat_name, prod_name):
        """ Remove our last offer only if it's the highest
        :param cat_name: category name
        :param prod_name: product name
        """
        try:
            cat = Category.search_category(self._auct._categories, cat_name)
            auct = cat.search_auction(prod_name)
            auct.unbid(self.user)
            self.response(1)
        except CategoryException, e:
            debug_print(e)
            self.response(0)
        except AuctionException, e:
            debug_print(e)
            self.response(3)

    @synchronized(myLock)
    def close_bid(self, cat_name, prod_name):
        """ Close a bid
        :param cat_name: category name
        :param prod_name: product name
        """
        print "Closing bid " + prod_name
        try:
            cat = Category.search_category(self._auct._categories, cat_name)
            auct = cat.search_auction(prod_name)
            auct.close(self.user)
            cat.del_auction(auct)
            self.response(1)
        except CategoryException, e:
            # Not matching category
            error_print(e)
            self.response(0)
        except AuctionException, e:
            # No Winner
            error_print(e)
            self.response(8)
        except ExistingAuctionException, e:
            #No auction
            error_print(e)
            self.response(5)
        except UserException, e:
            #User not allowed to close
            error_print(e)
            self.response(7)

    def response(self, response, res_msg="", token={}):
        """Compose a generic response
        :param response: response code
        :param res_msg: response message
        :param token: optional, token of the session
        """
        payload = {
            'msg_id': -1,
            'response': response,
        }
        if(res_msg):
            payload['res_msg'] = res_msg
        if(token):
            payload['token'] = token
        json_d = json.dumps(payload) + "\r\n"
        self._cs.send(json_d)
