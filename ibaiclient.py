import socket
import hashlib
import json
import threading
import Queue


class IbaiClient:
    def __init__(self, hostname='localhost'):
        """Initalize the Ibai client library.
        :param hostname: hostname of the client, default to localhost
        """
        self._serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._notify_hostname = hostname
        self._serverSocket.bind((hostname, 0))
        self._notify_port = self._serverSocket.getsockname()[1]
        self._token = ""
        self.notifications = Queue.Queue()

    def notify_worker(self):
        """notification thread that receive notifications and push them into a message queue  """
        self.notify_run = True
        self._serverSocket.listen(1)
        while self.notify_run:
            (clientsocket, address) = self._serverSocket.accept()
            msg = clientsocket.recv(1024)
            if msg == "":
                    self.notify_run = False
            else:
                msgs = msg.split('\r\n')
                for l in msgs:
                    json_d = json.loads(l)
                    if json_d['msg_id'] == 22:  # Notify
                        self.notifications.put(json_d)
                clientsocket.close()
        self._serverSocket.close()
        return

    def listen_notify(self):
        """Starts the notification worker and listens for notifications
        """
        self._nthread = threading.Thread(target=self.notify_worker)
        self._nthread.daemon = True
        self._nthread.start()

    def connect(self, address, port):
        """Connect to the server
        :param address: remote address of the server
        :param port:  remote port of the server
        :return:
        """
        self.sock = socket.socket()
        self.sock.connect((address, port))
        return True

    def disconnect(self):
        """ Disconnect the server"""
        self.sock.close()
        self._serverSocket.close()
        return True

    def send(self, data):
        """Send a dictionary to the server
        :param data: dictionary containing the message
        """
        json_d = json.dumps(data) + "\r\n"
        self.sock.send(json_d)

    def eval_res(self, opcode):
        """Receive a response and evaluate it
        :param opcode: code of the command we executed, if command is login set the token
        :return: response code
        """
        resp = self.sock.recv(1024)
        resp = resp.split("\r\n")
        json_resp = json.loads(resp[0])
        if json_resp['msg_id'] == -1:
            if opcode == 11:
                self._token = json_resp['token']
            return json_resp['response']
        else:
            raise Exception("Not a Response")

    def login(self, user, password):
        """Login to the remote server
        :param user: username
        :param password: password
        :return: result of the operation
        """
        pwd = hashlib.md5(password).hexdigest()
        user = user.lower()
        data = {
            'msg_id': 11,
            'user': user,
            'pass': pwd
        }
        self.send(data)
        return self.eval_res(data['msg_id'])

    def register(self, cat_name):
        """Register a new category
        :param cat_name: name of the category
        :return: result of the operation
        """
        data = {
            'token': self._token,
            'msg_id': 31,
            'category': cat_name
        }
        self.send(data)
        return self.eval_res(data['msg_id'])

    def sell(self, cat_name, prod_name, price):
        """Sell a new product inside a category
        :param cat_name: category of the product
        :param prod_name: name of the product
        :param price: base price for the auction
        :return: result of the operation
        """
        data = {
            'token': self._token,
            'msg_id': 41,
            'category': cat_name,
            'product': prod_name,
            'price': price
        }
        self.send(data)
        return self.eval_res(data['msg_id'])

    def bid(self, cat_name, prod_name, price):
        """Bid an existing product
        :param cat_name: category of the product
        :param prod_name: name of the product
        :param price: value of the bid
        :return:
        """
        data = {
            'token': self._token,
            'msg_id': 51,
            'category': cat_name,
            'product': prod_name,
            'price': price
        }
        self.send(data)
        return self.eval_res(data['msg_id'])

    def unbid(self, cat_name, prod_name):
        """Remove your bid, only if it's the last one
        :param cat_name: name of the cateogry
        :param prod_name: name of the product
        :return: result of the operation
        """
        data = {
            'token': self._token,
            'msg_id': 52,
            'category': cat_name,
            'product': prod_name,
        }
        self.send(data)
        return self.eval_res(data['msg_id'])

    def close(self, cat_name, prod_name):
        """Close the bid if you are the owner
        :param cat_name: name of the cateogry
        :param prod_name: name of the product
        :return: result of the operation
        """
        data = {
            'token': self._token,
            'msg_id': 53,
            'category': cat_name,
            'product': prod_name,
        }
        self.send(data)
        return self.eval_res(data['msg_id'])

    def notify_me(self):
        """Register the notification endpoint to the server
        :return: True if success, False otherwise
        """
        data = {
            'token': self._token,
            'msg_id': 21,
            'host': self._notify_hostname,
            'port': self._notify_port
        }
        self.send(data)
        try:
            response = self.notifications.get(timeout=2)
            print "Notifica: "+ response['text']
        except Queue.Empty:
            return False
        if response['msg_id'] == 22:
            if response['code'] == 1:
                return True
        return False
