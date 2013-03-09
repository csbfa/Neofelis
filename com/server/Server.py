"""

"""

import threading, sys, pickle, subprocess
import socketserver as ss

class NeofelisServerHandler(ss.BaseRequestHandler):
    """

    """

    def handle(self):

        # first receive params dictionary as pickled object
        self._data = self.request.recv(4096)

        try:
            # unpickle the dictionary
            self._params = pickle.loads(self._data)
        except pickle.PickleError:
            print("Pickle Error. Request for pickled object failed")
        finally:
            # response to client with boolean status of recv
            if not isinstance(self._params, dict):
                print("Invalid input to server")
                self.request.sendall(False)
                sys.exit(-1)

            self.request.sendall(True)

            # now receive pipeline client information as string
            self._client = self.request.recv(4096)

            # response to client with boolean status of recv
            if not isinstance(self._client, str):
                print("Invalid input to server")
                self.request.sendall(False)
                sys.exit(-1)

            self.request.sendall(True)

            # now get user for ssh call to pipeline client
            self._user = self.request.recv(4096)

            # response to client with boolean status of recv
            if not isinstance(self._user, str):
                print("Invalid input to server")
                self.request.sendall(False)
                sys.exit(-1)

            self.request.sendall(True)

            # finally, get the passwd to the pipeline client
            self._passwd = self.request.recv(4096)

            # response to client with boolean status of recv
            if not isinstance(self._user, str):
                print("Invalid input to server")
                self.request.sendall(False)
                sys.exit(-1)

            self.request.sendall(True)

            # start parallel server
            # run rypc code

            # deploy remote_pipe to client. This ensures that the file exists
            # do we need to check if python is installed? check if copy worked?
            # run remote_pipe with _params attached
            # way to get output?

            #self._s = ssh.Connection( self._client, username=self._user, password=self._passwd)
            #self._command = "python ", self.server.server_address
            # Need more error handling here.
            #self._result = self._s.execute(self._command)
            #print(self._result)
            #self._s.close()

            print("Under construction")

            # run Pipeline


class NeofelisServerThreader(ss.ThreadingMixIn, ss.TCPServer):
    pass

class NeofelisServer():
    """

    """

    def __init__(self, HOST=None, PORT=None):
        self.HOST = HOST
        self.PORT = PORT

        if self.HOST is None:
            self.HOST = "localhost"

        # force user to have provided port number
        if PORT is None:
            print("Error! PORT number not provided")
            sys.exit(-1)

        # start the server
        self._server = NeofelisServerThreader((self.HOST, self.PORT), NeofelisServerHandler)
        # add support for Server GUI?

    def start(self):

        # limit number of server threads?

        try:
            self._server_thread = threading.Thread(target=self._server.serve_forever)
            # Exit the server thread when the main thread terminates
            self._server_thread.daemon = True
            self._server_thread.start()
        except threading.ThreadError:
            print("Thread Error. I could recover here, but it's easier to make you try again.")
            sys.exit(-1)

        # start a new server console window on new thread, with instructions printed to console window.
        # new - starts a new Neofelis process, with "console" and "prompt"
        # stop - stops server
        # clear - clears window
        self._console = serverConsole(self._server)
        self._console.run()

class serverConsole(threading.Thread):
    """

    """
    def __init__(self, server):
        self._input = ""
        self._params = None
        threading.Thread.__init__(self)
        self._server = server

    def run(self):

        print("Neofelis Server\nCommands:\nnew - starts a new Neofelis to run on a client computer\nstop - stops the Neofelis Server\nclear - clears the console")

        while 1:

            self._input = input(":> ")
            while self._input == "": continue

            if self._input == "new":

                print("This is the server version of Neofelis\nInterface and Server options are automatically set.")

                # get server info
                self._ip, self._port = self._server.server_address

                # start new neofelis process - seperate terminal should pop open
                subprocess.Popen(["python Neofelis.py --server=", self._ip, "--port=", self._port, "--interface=console --prompt"])

            elif self._input == "clear":
                print(end="\r")
                sys.stdout.flush()

            elif self._input == "stop": break
            else: print("Input not recognized")

            self._input = ""

        self._server.shutdown()

if __name__ == "__main__":
    NeofelisServer()