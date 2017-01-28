import socket
import hashlib
import json
import threading
from time import sleep


class IbaiClient:
    def __init__(self, hostname):
        self._serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._notify_hostname = hostname
        self._serverSocket.bind((hostname, 0))
        self._notify_port = self._serverSocket.getsockname()[1]
        self.notifications = []

    def stop_notify_worker(self):
        print("Killing Worker")
        self.notify_run = False
        self._nthread.join()
        print("Killed Worker")

    def notify_worker(self):
        self.notify_run = True
        self._serverSocket.listen(1)
        while self.notify_run:
            print("Pre_accept")
            (clientsocket, address) = self._serverSocket.accept()
            print("Pre_receive")
            msg = clientsocket.recv(1024)
            print("Post_receive")
            if msg == "":
                self.notify_run = False
            else:
                if __debug__:
                    print msg
                msgs = msg.split('\r\n')
                for l in msgs:
                    json_d = json.loads(l)
                    print("NW2")
                    if json_d['msg_id'] == 40:  # Notify
                        print("NW3")
                        self.notifications.append(json_d)
                    else:
                        self.notify_run = False
        self._serverSocket.close()

    def listen_notify(self, host, port):
        self._nthread = threading.Thread(target=self.notify_worker)
        self._nthread.isDaemon = True
        self._nthread.start()

    def connect(self, address, port):
        self.sock = socket.socket()
        self.sock.connect((address, port))
        return True

    def disconnect(self):
        self.sock.close()
        return True

    def send(self, data):
        json_d = json.dumps(data) + "\r\n"
        if __debug__:
            print json_d
        self.sock.send(json_d)

    def eval_res(self, res_id):
        resp = self.sock.recv(1024)
        if __debug__:
            print resp
            print res_id
        resp = resp.split("\r\n")
        json_resp = json.loads(resp[0])
        if json_resp['msg_id'] == -1:
            if json_resp['response'] == res_id:
                return json_resp['code']
            else:
                raise Exception("Not a Response")
        else:
            raise Exception("Not a Response")

    def login(self, user, password):
        pwd = hashlib.md5(password).hexdigest()
        user = user.lower()
        data = {
            'msg_id': 0,
            'user': user,
            'pass': pwd
        }
        self.send(data)
        return self.eval_res(data['msg_id'])

    def register(self, cat_name):
        data = {
            'msg_id': 1,
            'category': cat_name
        }
        self.send(data)
        return self.eval_res(data['msg_id'])

    def sell(self, cat_name, prod_name, price):
        data = {
            'msg_id': 2,
            'category': cat_name,
            'product': prod_name,
            'price': price
        }
        self.send(data)
        return self.eval_res(data['msg_id'])

    def bid(self, cat_name, prod_name, price):
        data = {
            'msg_id': 3,
            'category': cat_name,
            'product': prod_name,
            'price': price
        }
        self.send(data)
        return self.eval_res(data['msg_id'])

    def notify_me(self):
        data = {
            'msg_id': 4,
            'host': self._notify_hostname,
            'port': self._notify_port
        }
        self.send(data)
        response = self.notifications.pop()
        if response['msg_id'] == 40:
            if response['notif_code'] == 11:
                print response['notif_msg']
                return True
        return False
