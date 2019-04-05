import socket
from datetime import datetime
import json
from slave import Slave

class DIPSlave(Slave):

    def generate_info_message(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"\nMy current IP is " + ip
        except Exception as e:
            return str(e)


if __name__ == "__main__":

    with open("auth.json", "r") as f:
        auth_dict = json.load(f)
        nickname, password = auth_dict["nickname"], auth_dict["password"]
        server_address, server_port = auth_dict["server_address"], auth_dict["server_port"]

    dip = DIPSlave(nickname, password, server_address, server_port)

    dip.launch()
    dip.join()



