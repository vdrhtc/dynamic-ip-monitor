import socket
import urllib.request
from datetime import datetime
from threading import Thread
from time import sleep
import ssl
import json

from loggingserver import LoggingServer

class DIPClient:

    def __init__(self, nickname, password, server_address, server_port):

        self._server_address = server_address
        self._password = password
        self._server_port = server_port
        self._nickname = nickname
        self._logger = LoggingServer.getInstance("dip-client")

        self._context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self._context.verify_mode = ssl.CERT_REQUIRED
        certurl = "https://raw.githubusercontent.com/vdrhtc/overseer/master/domain.crt"
        self._certfile = urllib.request.urlretrieve(certurl)[0]
        self._context.load_verify_locations(self._certfile)

        self._secure_socket = self._context.wrap_socket(socket.socket())  # instantiate

        self._secure_socket.connect((server_address, server_port))  # connect to the server

        self._stop = False
        self._updater = Thread(target=self._act)
        self._updater.setDaemon(True)

        self._strategies = {"update": self._send_update,
                            "reconnect": self._reconnect,
                            "handshake": self._handshake}
        self._current_strategy = "handshake"

    def launch(self):
        self._stop = False
        self._updater.start()

    def join(self):
        self._updater.join()

    def _act(self):
        while not self._stop:
            try:
                self._strategies[self._current_strategy]()
            except (TimeoutError, ConnectionRefusedError, ConnectionResetError, ConnectionAbortedError, ConnectionError) as e:
                self._logger.warn(str(e))
                sleep(15)
                self._current_strategy = "reconnect"
            except Exception as e:
                self._logger.warn(str(e))
                print(e)
                break

        self._secure_socket.close()

    def _send_update(self):
        print("\rSending update, " + str(datetime.now()), end="")
        try:
            data = self.generate_info_message().encode()
        except Exception as e:
            data = str(e).encode()

        self._secure_socket.send(data)
        sleep(15)

    def _reconnect(self):
        print("\rReconnecting...", end="")
        
        self._secure_socket.close()
        self._secure_socket = self._context.wrap_socket(socket.socket())
        self._secure_socket.connect((self._server_address, self._server_port))  # connect to the server
        self._current_strategy = "handshake"

    def _handshake(self):
        self._secure_socket.send((self._nickname+"\r\n"+self._password).encode())
        response = self._secure_socket.recv(1024).decode()
        if response == self._nickname:
            self._current_strategy = "update"
            print("Successful handshake!")
        else:
            print(" "+response, end="")
            self._current_strategy = "reconnect"
            sleep(15)

    def generate_info_message(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return "My current IP is " + ip


if __name__ == "__main__":

    with open("auth.json", "r") as f:
        auth_dict = json.load(f)
        nickname, password = auth_dict["nickname"], auth_dict["password"]
        server_address, server_port = auth_dict["server_address"], auth_dict["server_port"]


    dip = DIPClient(nickname, password, server_address, server_port)

    dip.launch()
    dip.join()



