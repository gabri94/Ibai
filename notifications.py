import threading
import socket
import json


class NotificationsThread(threading.Thread):

    def __init__(self, hostname, port):
        threading.Thread.__init__(self)
        self._serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._serverSocket.bind((hostname, port))
        self.port = self._serverSocket.getsockname()[1])

    def run(self):
        go = True
        self._serverSocket.listen(1)
        t = threading.currentThread()
        while getattr(t, "run", True) and go:
            (clientsocket, address) = self._serverSocket.accept()
            msg = cs.recv(1024)
            if msg == "":
                go = False
            else:
                if __debug__:
                    print msg
                msgs = msg.split('\r\n')
                msgs.pop()  # remove last msg
                for l in msgs:
                    json_d = json.loads(line)
                    if json_d['msg_id'] == 10:  # Notify
                        print json_d
