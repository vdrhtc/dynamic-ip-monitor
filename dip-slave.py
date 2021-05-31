import socket
from datetime import datetime
import json
from slave import Slave
from requests import get
import netifaces as ni
class DIPSlave(Slave):

    def generate_info_message(self):
        try:
            ip = get('https://api.ipify.org').text
            ni.ifaddresses('enp67s0')
            ip_internal = ni.ifaddresses('enp67s0')[ni.AF_INET][0]['addr']
            return "My current IP is " + ip + " or "+str(ip_internal) +" (" \
                                                                       "local)"
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



