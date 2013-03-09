"""

"""

# reroute print if GUI

import socket, pickle
#from PyQt4 import QtCore, QtGui

class NeofelisView:
    """

    """

    def __init__(self, type):
        self._type = type
        self._client = None

    def new(self, tab=False):
        pass

        # self.process = QProcess() ONLY IF MAIN GUI WINDOW. Thread if tab
        # main gui calls process automagically. process will be called externally for tab ( due to server nature )

    def process(self):
        pass
        # return new params dictionary

    def setClient(self, client):
        self._client = client

    def getClient(self,):
        pass
        # return client

    def getType(self):
        return self._type

    def prompt(self, message):
        if self._type == "console":
            return input(message)
        else: pass

def client(self, params, client, address, port):

    self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self._socket.connect((address, port))
    try:
        self._data = pickle.dumps(params)
        self._socket.sendall(self._data)
    except socket.error:
        print("Socket Error: Failure to send parameters to server\n\tat Neofelis.new(), line 93")
    finally:
        self._receive = self._socket.recv(4096)
        if not self._receive:
            print("Failed to transfer command line options to server. Please try again.")

    try:
        self._socket.sendall(client)
    except socket.error:
        print("Socket Error: Failure to send client location to server\n\tat Neofelis.new(), line 103")
    finally:
        self._receive = self._socket.recv(4096)
        if not self._receive:
            print("Failed to transfer client location.")
        self._socket.close()
