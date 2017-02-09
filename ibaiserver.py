import socket
import threading
import hashlib
import random
from client_manager import ClientManager
from category import Category
from auction import Auction
from user import User

class Ibai:
    '''
    This class runs an auction server on the specified port
    The method listen loops waiting for new connections and each time a client
    connects a new ClientManager istance is created to handle it.
    '''
    def __init__(self, hostname, port):
        self._users = {}
        self._categories = {}
        self._serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.seed_users()
        self.seed_categories()
        self._key = hashlib.md5(str(random.getrandbits(1024))).hexdigest()
        self._serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._serverSocket.bind((hostname, port))
        self._serverSocket.listen(5)

    def seed_users(self):
        pwd = hashlib.md5("pippopippo").hexdigest()
        self._users['gabriel'] = User("gabriel", pwd, "13-12-1994")
        pwd = hashlib.md5("gabrigabri").hexdigest()
        self._users['pippo'] = User("pippo", pwd, "13-12-1294")

    def seed_categories(self):
        cat_l = Category("libri")
        a = Auction("Il Signore degli anelli", 10, "pippo")
        b = Auction("La Metamorfosi", 7, "pippo")
        cat_l.add_auction(a)
        cat_l.add_auction(b)
        self._categories['libri'] = cat_l
        cat_v = Category("vestiti")
        c = Auction("Smoking nero usato", 500, "pippo")
        d = Auction("Scarpe in pelle", 70, "pippo")
        cat_v.add_auction(c)
        cat_v.add_auction(d)
        self._categories['vestiti'] = cat_v

    def listen(self):
        self.clients = []
        while(True):
            (clientsocket, address) = self._serverSocket.accept()
            cm = ClientManager(clientsocket, address, self)
            cm.daemon = True
            self.clients.append(cm)
            cm.start()

e = Ibai('localhost', 7652)
e.listen()
