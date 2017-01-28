from category import Category
from auction import Auction
import json
import threading
from threading import Lock
import socket


def synchronized(lock):
    """ Synchronization decorator. """

    def wrap(f):
        def newFunction(*args, **kw):
            if __debug__:
                print("LOCKING")
            lock.acquire()
            if __debug__:
                print("LOCKED")
            try:
                return f(*args, **kw)
            finally:
                if __debug__:
                    print("UNLOCKING")
                lock.release()
                if __debug__:
                    print("UNLOCKED")
        return newFunction
    return wrap


myLock = Lock()

class ClientManager(threading.Thread):

    def __init__(self, cs, address, auct):
        threading.Thread.__init__(self)
        self._auct = auct
        self._address = address
        self._cs = cs
        self.notif_sock = socket.socket()
        self.logged = False

    def run(self):
        if __debug__:
            print("Thread started")
        go = True
        while(go):
            msg = self._cs.recv(1024)
            if msg == "":
                go = False
            else:
                if __debug__:
                    print msg
                msgs = msg.split('\r\n')
                msgs.pop()  # remove last msg
                for l in msgs:
                    go = self.read_command(l)
        self._cs.close()
        if __debug__:
            print("Thread stopped")

    def read_command(self, line):
        json_d = json.loads(line)
        if json_d['msg_id'] == 0:  # Login
            self.login((None, json_d['user'], json_d['pass']))
            return True
        if self.logged:
            if json_d['msg_id'] == 1:  # Register category
                self.register((None, json_d['category']))
                return True
            if json_d['msg_id'] == 2:  # Register auction
                self.sell((None, json_d['category'], json_d['product'], json_d['price']))
                return True
            if json_d['msg_id'] == 3:  # Make a bid
                self.buy((None, json_d['category'], json_d['product'], json_d['price']))
                return True
            if json_d['msg_id'] == 4:  # Register the endpoint for push notif
                self.notify((None, json_d['host'], json_d['port']))
                return True
        return False

    def login(self, args):
        username = args[1].lower()
        try:
            u = self._auct._users[username]
            if u['pwd'] == args[2]:
                # Login effettuato
                self.logged = True
                self.response(0, 1)
                return True
        except KeyError, e:
            print "Utente non trovato"
        self.response(0, 0)
        return False

    def notify(self, args):
        self.remote_host = args[1]
        self.remote_port = args[2]
        if self.notification(11, 'Notification Connected'):
            self.response(4, 1)
            return True
        else:
            self.response(4, 0)
            return False

    @synchronized(myLock)
    def register(self, args):
        cat_name = args[1].lower()
        try:
            c = self._auct._categories[cat_name]
            raise Exception("Categoria gia' esistente")
        except KeyError, e:
            try:
                self._auct._categories[cat_name] = Category(cat_name)
            except Exception, e:
                print "Errore: " + str(e)
                self.response(1, 0)
            else:
                self.response(1, 1)
        except Exception, e:
            self.response(1, 0)
            print "Errore: " + str(e)

    @synchronized(myLock)
    def sell(self, args):
        try:
            cat = Category.search_category(self._auct._categories, args[1])
            if not cat:
                raise Exception("Category not found")
            a = Auction(args[2], int(args[3]))
            cat.add_auction(a)
            self.response(2, 1)
        except KeyError, e:
            print "Categoria non trovata"
            self.response(2, -1)
        except Exception, e:
            print "Errore" + str(e)
            self.response(2, 0)

    @synchronized(myLock)
    def buy(self, args):
        try:
            cat = Category.search_category(self._auct._categories, args[1])
            if not cat:
                raise Exception("Category not found")
            auct = cat.search_auction(args[2])
            if not auct:
                raise Exception("Auction not found")
            auct.bid(args[3])
            self.response(3, 1)
        except KeyError, e:
            print "Categoria non trovata"
            self.response(3, -1)
        except Exception, e:
            if __debug__:
                print "Errore: " + str(e)
            self.response(3, 0)

    def error(self, id):
        print("Error : " + str(id))

    def notification(self, code, msg):
        try:
            if __debug__:
                print("Connecting to notif sock")
            self.notif_sock.connect((self.remote_host, self.remote_port))
            payload = {
                'msg_id': 40,
                'notif_code': code,
                'notif_msg': msg
            }
            json_d = json.dumps(payload)
            if __debug__:
                print("Sending to notif sock")
            self.notif_sock.send(json_d)
            self.notif_sock.close()
            if __debug__:
                print("Closed socket")
            return True
        except Exception, e:
            if __debug__:
                print "Errore: " + str(e)
            return False

    def response(self, res_id, res_code, res_msg=False):
        payload = {
            'msg_id': -1,
            'response': res_id,
            'code': res_code
        }
        if(res_msg):
            payload['res_msg'] = res_msg
        json_d = json.dumps(payload)
        self._cs.send(json_d)
