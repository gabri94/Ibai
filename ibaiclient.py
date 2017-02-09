import socket
import hashlib
import json
import threading
import Queue
from time import sleep


class IbaiClient:
    def __init__(self, hostname):
        self._serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._notify_hostname = hostname
        self._serverSocket.bind((hostname, 0))
        self._notify_port = self._serverSocket.getsockname()[1]
        self._token = ""
        self.notifications = Queue.Queue()

    def notify_worker(self):
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
                        if(json_d['code'] == -1):
                            self.notify_run = False
                        else:
                            self.notifications.put(json_d)
                    else:
                        self.notify_run = False
                clientsocket.close()
        self._serverSocket.close()
        return

    def listen_notify(self, host, port):
        self._nthread = threading.Thread(target=self.notify_worker)
        self._nthread.daemon = True
        self._nthread.start()

    def connect(self, address, port):
        self.sock = socket.socket()
        self.sock.connect((address, port))
        return True

    def disconnect(self):
        self.sock.close()
        self._serverSocket.close()
        return True

    def send(self, data):
        json_d = json.dumps(data) + "\r\n"
        self.sock.send(json_d)

    def eval_res(self, opcode):
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
        pwd = hashlib.md5(password).hexdigest()
        user = user.lower()
        data = {
            'msg_id': 11,
            'user': user,
            'pass': pwd
        }
        self.send(data)
        self.res = self.eval_res(data['msg_id'])
        return self.res

    def register(self, cat_name):
        data = {
            'token': self._token,
            'msg_id': 31,
            'category': cat_name
        }
        self.send(data)
        return self.eval_res(data['msg_id'])

    def sell(self, cat_name, prod_name, price):
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
        data = {
            'token': self._token,
            'msg_id': 51,
            'category': cat_name,
            'product': prod_name,
            'price': price
        }
        self.send(data)
        return self.eval_res(data['msg_id'])

    def notify_me(self):
        data = {
            'token': self._token,
            'msg_id': 21,
            'host': self._notify_hostname,
            'port': self._notify_port
        }
        self.send(data)
        try:
            response = self.notifications.get(timeout=10)
        except Queue.Empty:
            return False
        if response['msg_id'] == 22:
            if response['code'] == 1:
                return True
        return False
