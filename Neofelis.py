
import sys, getopt, re, os, socket, signal, logging, pickle
import com.pipeline.Pipeline as Pipeline
import com.view.View as View
import com.server.Ping as Ping
import com.exceptions as Exceptions
import com.utils.Utils as Utils
import com.log.Log as Log
import com.post.Progress as Progress


class Neofelis():
    """
    OWNER

        Matthew Sullivan

    AUTHOR

        Brandon Webb
        Jarl Haggerty

    SYNOPSIS

        python Neofelis.py [prefix: -|--] [h|help] [m|man] [i|interface=] [x:|matrix=] [d:|database] [g:|genemark=] [b:blast=]
                           [e:|e-value=] [l:|min-length=] [t:|transterm=] [p:|promoter-score-cutoff=] [s:|scaffolding-distance=]
                           [input-file=] [input-dir=] [o:|output=] [email=] [s:|server=] [r:|port=] [smtp-server=] [smtp-user=]
                           [smtp-password=] [a:|trna-scan=] [prompt] [parse=] [save=] [log=]

    DESCRIPTION

        Developer's Note:

        Program Description:

        Options:

        -h --help                    Print Usage
        -m --man                     Print POSIX Manual
        -i --inferace                Specify 'console' or 'GUI' mode

        -x --matrix                  Matrix with which to run genemark
        -d --database                Database to use when running blast
        -g --genemark                Location of Genemark
        -b --blast                   Location of Blast+
        -e --e-value                 Minimal evalue for any genes detected
        -l --min-length              Minimum length of any genes discovered
        -t --transterm               Location of Transterm
        -p --promoter-score-cutoff   Minimum promoter score of any promoters selected from a promoter search
        -s --scaffolding-distance    Distance to allow between genes when determining scaffolds
        -a --trna-scan               Location of tRNAscan

        --input_dir                  Specify the input directory containing the source files for processing. If multiple files
                                       need to be processed, use this option

        --input_file                 Specify a single input file for processing

        -o --output                  Specify the output directory

        -s --server                  Specify the server address ( either ip or hostname ) to connect to or setup. If the
                                       server is not alive, Neofelis will prompt the user to start a new server. If the required
                                       Neofelis parameters are specified, then Neofelis will prompt the user to run the parameters
                                       on the server. If no parameters are specified, then Neofelis will assume to start a clean server.
        -r --port                    Port number of the server to connect on

        --email                      Email address that will be emailed when query is processed.
        --smtp-server                The smtp to use to send emails when the pipeline.py processes a genome.
        --smtp-user                  User name for the smtp server.
        --smtp-password              Password for the smtp server.

        --prompt                     Prompt for command line options ( console mode only )
        --parse                      Parse file for command line options
        --save                       Save provided command line options to file

        --log                        Specify the logging level to run Neofelis with:
                                        CRITICAL - Log Critical message ( full library debugging purposes )
                                        DEBUG - Default. Log error messages.
                                        NOTSET - No logging

    EXIT STATUS

        Neofelis dies on any unrecoverable error

    EXAMPLES

    CHANGE LOG

    COPYRIGHT

        Permission is granted to copy, distribute and/or modify this document under the terms of the GNU Free Documentation
        License, Version 1.2 or any later version published by the Free Software Foundation; with no Invariant Sections, with
        no Front-Cover Texts, and with no Back-Cover Texts.

    """

    def __init__(self):
        pass

    usage = "python Neofelis.py [prefix: -|--] [h|help] [m|man] [i|interface=] [x:|matrix=] [d:|database] [g:|genemark=] " \
            "\n\t\t   [b:blast=] [e:|e-value=] [l:|min-length=] [t:|transterm=] [p:|promoter-score-cutoff=] " \
            "\n\t\t   [s:|scaffolding-distance=] [input_file=] [input_dir=] [o:|output=] [email=] [s:|server=] [r:|port=] " \
            "\n\t\t   [smtp-server=] [smtp-user=] [smtp-password=] [a:|trna-scan=] [prompt] [parse=] [save=] [u|qsub]"

    LEVELS = {'debug': logging.DEBUG,
              'info': logging.INFO,
              'warning': logging.WARNING,
              'error': logging.ERROR,
              'critical': logging.CRITICAL}

    def start_server(self, params, view):
        """
        Method: start_server ( dict, NeofelisView ):
            Attempts to start a new Neofelis server at the address specified in option 'server', listening on port
            specified in option 'port='. If the server is already running, then the server input is ignored. If any
            additional parameters are specified and the view is of type console, then the user is prompted to pass the
            params to the server to be run on a new client. If the view is of type GUI, then the additional parameters
            is ignored.
        """

        print("Under Construction")
        exit(-1)

        self._params = params
        self._view = view

        # ping server address to see if server is running or not
        self._alive = self.test(self._params["server"])

        if not self._alive:

            self._response = self._view.prompt("Would you like to start a new Neofelis server at ", self._params["server"], "? [y/n]")
            if re.match(r'y|yes', self._response, re.IGNORECASE):
                self._user = self._view.prompt("User: ")
                self._pass = self._view.prompt("Password: ")
                #self._s = Connection(self._params["server"], username=self._user, password=self._pass)
                #self._command = "python Server.py ", self._params["server"], " ", self._params["port"]
                #self._s.execute(self._command) # we will need the full path
                #self._s.close()
                print ( "Under construction due to versioning conflictions")

        else:
            print("Server on this address is already running")


        if len(self._params) > 3 and self._view == "console":
            self._response = view.prompt("Additional input was detected. Would you like the server to handle this input, or continue processing on this computer? [y/n]")
            if re.match(r'y|yes', self._response, re.IGNORECASE):
                self._client = view.prompt("Please specify client address or hostname to run Neofelis on")
                self._user = view.prompt("Please specify client login name")
                self._pass = view.prompt("Please specify client password")
                self.client(self._params, self._client, self._user, self._pass, self._params["server"], self._params["port"])
                sys.exit(1)

    # start_server

    def client(self, params, client, user, passwd, address, port):
        """
        Method: Client ( dict, string, string, string, string, string ):
            Given the client address, client user, client password, Neofelis server address, and Neofelis port,
            Client attempts to open a new socket to the Neofelis server. Once a connection is made, Client sends
            a pickled object of params ( type dict ) and the client info to the server.
        """

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
                self._socket.close()

        try:
            self._socket.sendall(client)
        except socket.error:
            print("Socket Error: Failure to send client location to server\n\tat Neofelis.new(), line 103")
        finally:
            self._receive = self._socket.recv(4096)
            if not self._receive:
                print("Failed to transfer client location.")
                self._socket.close()

        try:
            self._socket.sendall(user)
        except socket.error:
            print("Socket Error: Failure to send client location to server\n\tat Neofelis.new(), line 103")
        finally:
            self._receive = self._socket.recv(4096)
            if not self._receive:
                print("Failed to transfer client location.")
                self._socket.close()

        try:
            self._socket.sendall(passwd)
        except socket.error:
            print("Socket Error: Failure to send client location to server\n\tat Neofelis.new(), line 103")
        finally:
            self._receive = self._socket.recv(4096)
            if not self._receive:
                print("Failed to transfer client location.")
                self._socket.close()

        self._socket.close()

    # client

    def test(self, address):
        """
        Method: test ( string ):
            Pings the address. Returns true if the server is alive, false otherwise.
        """
        try:
            Ping.verbose_ping(address)
        except socket.error:
            return False
        finally:
            return True

    # test

    def to_string(self):
        """
        Method: to_string ():
            Return full POSIX documentation formatted to string
        """
        return '{0}'.format(Neofelis.__doc__)

    # toString

    def signal_handler(self, signal, frame):
        print("Keyboard Interupt caught\n")
        if self.pipe is not None:
            self.pipe.panic()

        sys.exit(0)

    def main(self, argv=None):
        """
        Method: main ():
            Main method for Neofelis. Contains the command line input parsing and validation.
            If the interface type is 'GUI', then all additional parameters - expect server parameters - are ignored and
            main attempts to start a new GUI window. If the interface type is 'console', then main continues processing
            all input parameters.
        """

        signal.signal(signal.SIGINT, self.signal_handler)

        self._params = {
            "help"                  : False,
            "man"                   : False,
            "server"                : None,
            "port"                  : None,
            "interface"             : "gui",
            "matrix"                : None,
            "database"              : None,
            "genemark"              : None,
            "blast"                 : None,
            "e-value"               : None,
            "min-length"            : None,
            "transterm"             : None,
            "promoter-score-cutoff" : None,
            "scaffolding-distance"  : None,
            "input_file"            : None,
            "input_dir"             : None,
            "output"                : None,
            "trna-scan"             : None,
            "email"                 : None,
            "smtp_server"           : None,
            "smtp_user"             : None,
            "smtp_password"         : None,
            "prompt"                : None,
            "parse"                 : None,
            "save"                  : None,
            "qsub"                  : False,
            "log"                   : None
        }

        if argv is None or len(argv) == 1:

            # check if screen is capable of GUI ( GUI is default action when program is run )
            #try:
                # call GUI and ignore rest of input ( if applicable )
                #self._view = NeofelisView("GUI")
                # start GUI

            #except GraphicsException:
                self._params = Utils.Prompt(self._params)

        else:

            try:
                opts, args = getopt.getopt(argv[1:], "hmui:s:r:x:d:g:b:e:l:t:p:s:a:o:",
                    ["help", "man", "interface=", "matrix=", "database=", "genemark=", "blast=", "e-value=", "min-length=",
                    "transterm=", "promoter-score-cutoff=", "scaffolding-distance=", "input_file=", "input_dir=", "output=", "email=",
                    "server=", "port=", "smtp-server=", "smtp-user=", "smtp-password=", "trna-scan=", "prompt", "parse=", "save=", "qsub", "log="])

            except getopt.GetoptError as err:
                print(err)
                print(Neofelis.usage)
                return -1

            if opts is None or len(opts) == 0:
                print("Error: invalid input")
                return -1

            for k, v in opts:
                k = re.sub('^-{1,2}', '', k )
                k = re.sub('=', '', k)

                short = Utils.ShortOptions(self, k)

                if k in self._params:

                    if k == "help" or k == "man" or k == "qsub":
                        v = True
                    else:
                        v = v.rstrip('/')
                        v = v.rstrip('\\')
                    self._params[k] = v

                elif short in self._params:

                    if short == "h" or short == "m" or short == "u":
                        v = True
                    else:
                        v = v.rstrip('/')
                        v = v.rstrip('\\')
                    self._params[short] = v

                else:
                    assert False, ("Invalid option specified", k)

        print(self._params["qsub"])

        if self._params["help"]:
            print(Neofelis.usage)
            return 1

        if self._params["man"]:
            print(self.to_string())
            return 1

        if not re.match(r'^(console)$', self._params["interface"], re.IGNORECASE) and not re.match(r'^(gui)$', self._params["interface"], re.IGNORECASE):
            print("Invalid interface option")
            print(Neofelis.usage)
            return -1

        if not self._params["qsub"]:
            TITLE = '\n\n${BOLD}${BLACK}%s${NORMAL}\n\n'
            BODY = '${NORMAL}${BLACK}%s${NORMAL}\n\n'

            title = "Neofelis Application"
            body = "Permission is granted to copy, distribute and/or modify this document under the terms\nof the " \
                    "GNU Free Documentation License, Version 1.2 or any later version published by\nthe Free Software " \
                    "Foundation; with no Invariant Sections, with no Front-Cover Texts,\nand with no Back-Cover Texts." \
                    "\n\nInitializing program..."

            term = Progress.TerminalController()
            header = term.render(TITLE % title)
            content = term.render(BODY % body)
            sys.stdout.write(header)
            sys.stdout.write(content)

        # start logging
        try:
            self._log = Log()
            self._log.start(self.LEVELS.get(str(self._params("log")).lower(), logging.ERROR))
        except Exceptions.LoggingException:
            return -1

        self._logger = self._log.new(__name__)
        self._logger.info("Logging started with level %s", str(self._params("log")).upper())

        # different than default action - input parameters AND GUI allowed
        if re.match(r'gui', self._params["interface"], re.IGNORECASE):

            # check if screen is capable of GUI
            try:
                # call GUI and ignore rest of input, except server
                self._view = View.NeofelisView("GUI")

                # If server is specified, attempt to connect to the server ( given ip or hla ).
                # If no connection could be made, start a new server at that address
                # If additional input was specified, ask user if they want the server to handle processing
                #    if yes, pass off params to server and open a new server window ( allows user to choose where to run neofelis)
                #    if no, continue running locally
                if self._params["server"]: self.start_server(self._params, self._view)
                self._view.new()
                return 0
                # send filled out params to server in View

            except Exceptions.GraphicsException:
                print("PyQT is not enabled for your environment")

        else:

            self._view = View.NeofelisView("console")

            if self._params["input_file"] is not None and self._params["input_dir"] is not None:
                print("Invalid input: Cannot specify input file and input directory together")
                return -1

            ## If server is specified, attempt to connect to the server ( given ip or hla ).
            # If no connection could be made, start a new server at that address
            # If additional input was specified, ask user if they want the server to handle processing
            #    if yes, pass off params to server and open a new server window ( allows user to choose where to run neofelis)
            #    if no, continue running locally
            if self._params["server"]: self.start_server(self._params, self._view)

            #if self._params["prompt"]:
            #    self._params = Prompt(self, self._params)
            #elif self._params["parse"]:
            #   self._params = Parse(self, self._params)

            self._home = os.getenv('HOME')

            if not self._params["blast"]:
                self._params["blast"] = self._home + "/blast"
            else:
                if not os.path.exists(self._params["blast"] + "/bin/blastp"):
                    print("BLASTp not found at path: ", self._params["blast"] + "/bin/blastp")
                    return -1

            if not self._params["database"]:
                self._params["database"] = self._home + "/db/"
            else:
                #if not os.path.exists(self._params["database"]):
                #    print("Database not found at path: ", self._params["database"])
                #    return -1
                pass

            if not self._params["genemark"]:
                self._params["genemark"] = self._home + "/genemark"
            else:
                if not os.path.exists(self._params["genemark"] + "/gm"):
                    print("Genemark not found at path: ", self._params["genemark"] + "/gm")
                    return -1

            if not self._params["transterm"]:
                self._params["transterm"] = self._home + "/transterm"

            if not self._params["trna-scan"]:
                self._params["trna-scan"] = self._home + "/tRNAscan"
            else:
                if not os.path.exists(self._params["trna-scan"] + "/tRNAscan-SE"):
                    print("tRNAscan-SE not found at path: ", self._params["trna-scan"] + "/tRNAscan-SE")
                    return -1

            if not self._params["input_file"] and not self._params["input_dir"]:
                print("No fasta input was provided")
                return -1

            if self._params["input_file"]:
                self._params["input_file"] = Utils.FileIO(self, input_file = self._params["input_file"])

            if self._params["input_dir"]:
                self._params["input_dir"] = Utils.FileIO(self, input_dir = self._params["input_dir"])

            if self._params["output"]:
                self._params["output"] = Utils.FileIO(self, output_dir= self._params["output"])
            else:
                print("no report output was provided")
                return -1

            #if self._params["save"]:
                #Save(self, self._params)

            # set up for multiprocessing
            self.pipe = Pipeline.NeofelisPipeline()
            self.pipe.run(self._params)

            logging.shutdown()

            return 0

    # main

# main catch
if __name__ == "__main__":
    
            #print("\nNOTES:\n\nTODO: BLAST+, .00 suffix and validation check when the suffix is present")
        #print("TODO: propagate pipeline thread instance among all sub classes for termination check")
        #print("TODO: Prompt, parse, and save")
        #print("TODO: overwrite lines rather than append to STDOUT")
        #print("TODO: over reporting number of failed files")
        #print("TODO: overwrite xml files if empty")
        #print("TODO: ignore non fasta files in inital processing")
        #print("TODO: check cores")
        #print("TODO: better way to terminate program inside methods")

        #print("TODO: check logging")
        #print("TODO: error msg # enum")
        #print("TODO: pass exception msg to parent")
        #print("TODO: thread safety for logging")

    sys.exit(Neofelis().main(sys.argv))