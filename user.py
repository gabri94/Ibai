import socket
import json


class User:
    def __init__(self, name, pwd, date):
        self.name = name
        self.password = pwd
        self.date = date
        self.hostname = ""
        self.port = 0

    def update_notif_socket(self, hostname, port):
        self.remote_host = hostname
        self.remote_port = port

    def notify(self, code, msg):
        self.notif_sock = socket.socket()
        self.notif_sock.connect((self.remote_host, self.remote_port))
        payload = {
            'msg_id': 22,
            'code': code,
            'text': msg
        }
        json_d = json.dumps(payload)
        self.notif_sock.send(json_d)
        self.notif_sock.close()
