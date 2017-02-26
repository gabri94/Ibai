import socket
import json


class User:
    def __init__(self, name, pwd, date):
        """Create a new User
        :param name: Unique username of the user
        :param pwd: MD5 hash of the password
        :param date: registration date
        """
        self.name = name
        self.password = pwd
        self.date = date
        self.remote_host = ""
        self.remote_port = 0

    def __repr__(self):
        return self.name
    def __str__(self):
        return self.__repr__()

    def update_notif_socket(self, hostname, port):
        """Update the client remote host for the notifications
        :param hostname: hostname of the client
        :param port: port for the notifications on the client
        :return:
        """
        self.remote_host = hostname
        self.remote_port = port

    def notify(self, code, msg):
        """Notify the user
        :param code: notification code
        :param msg: notification message
        """
        if not self.remote_port:
            return
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
