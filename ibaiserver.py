import hashlib
import random
import socket
from model.user import User
from model.category import Category
from model.auction import Auction
from client_manager import ClientManager



class IbaiServer:
    """
    This class runs an auction server on the specified port
    The method listen loops waiting for new connections and each time a client
    connects a new ClientManager is instanced to handle it.
    """
    def __init__(self, hostname, port):
        """Initalize the IbaiServer
        :param hostname: hostname where the server will listen
        :param port: port for the server
        """
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
        """Seed the database with 2 users    """
        pwd = hashlib.md5("pippopippo").hexdigest()
        self._users['gabriel'] = User("gabriel", pwd, "13-12-1994")
        pwd = hashlib.md5("gabrigabri").hexdigest()
        self._users['pippo'] = User("pippo", pwd, "13-12-1294")

    def seed_categories(self):
        """Seed the  database with some products and categories"""
        cat_l = Category("libri")
        pippo = self._users['pippo']
        a = Auction("Il Signore degli anelli", 10, pippo)
        b = Auction("La Metamorfosi", 7, pippo)
        cat_l.add_auction(a)
        cat_l.add_auction(b)
        self._categories['libri'] = cat_l
        cat_v = Category("vestiti")
        c = Auction("Smoking nero usato", 500, pippo)
        d = Auction("Scarpe in pelle", 70, pippo)
        cat_v.add_auction(c)
        cat_v.add_auction(d)
        self._categories['vestiti'] = cat_v


    def listen(self):
        """Listen for the client connection and it to client_manager"""
        self.clients = []
        while(True):
            (clientsocket, address) = self._serverSocket.accept()
            cm = ClientManager(clientsocket, address, self)
            cm.daemon = True
            self.clients.append(cm)
            cm.start()

if __name__ == "__main__":
    e = IbaiServer('localhost', 7652)
    e.listen()


