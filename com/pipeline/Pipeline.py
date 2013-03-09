"""

"""

import os
import Library.Monitor as monitor
import Library.Event as event
from threading import ThreadError
from Library.Progress import *
from Library.Utils import *

class NeofelisPipeline():
    """

    """

    def __init__(self):

        self._sentinel = None
        self._pool = []
        self._params = None
        self._file = None
        self._is_updated = False
        self._failed = 0
        self._completed = 0
        self._threadstat = {}

    def status(self, threadName):
        """
        Return an instance of threadstat
        """

        return self._threadstat[threadName]

    def updateStatus(self, threadName, progress):
        """

        """

        self._threadstat[threadName] = progress
        self._is_updated = True

    def removeStatus(self, threadName):
        """

        """

        del self._threadstat[threadName]
        self._is_updated = True

    def getCompleted(self):
        """

        """

        return self._completed

    def incrementCompleted(self):
        """

        """

        self._completed += 1
        self._is_updated = True

    def getFailed(self):
        """

        """

        return self._failed

    def incrementFailed(self):
        """

        """

        self._failed += 1

    def size(self):
        """
        Return size of thread pool
        """

        return len(self._pool)

    def pool(self):
        """
        Return an instance of the thread pool
        """

        return self._pool

    def push(self, thread):
        """
        Push a thread into the thread pool
        """

        self._pool.append(thread)

    def remove(self, thread):
        """
        Remove thread from thread pool
        """

        try:
            self._pool.remove(thread)
        except ValueError:
            pass

    def is_active(self):
        """
        Return true if the thread pool contains elements, false otherwise
        """

        return len(self._pool) != 0

    def isUpdated(self):
        """
        Return the event status of the pipeline. To be replaced by a more mature notify system
        """

        return self._is_updated

    def reset(self):
        """

        """

        self._is_updated = False

    def panic(self):
        """

        """

        print("Shutting down. Press ctrl-c again for immediate termination")
        if self._sentinel.is_alive:
            for thread in self.pool():
                if thread.isAlive:
                    print("Joining thread ", thread.name, end="\n")
                    thread.stop()
                    thread.join()

            print("Joining the sentinel thread...")
            if self._sentinel.is_alive:
                try:
                    self._sentinel.join()
                except Exception:
                    pass

            print("Shutdown complete\n")

    def run(self, params):
        """"

        """

        self._params = params
        self._queries = []

        if not self._params["qsub"]:
            self.BODY = '${BOLD}${BLACK}%s${NORMAL}\n\n'
            self.body = "Pipeline processing is starting"
            self.term = TerminalController()
            self.content = self.term.render(self.BODY % self.body)
            sys.stdout.write(self.content)

        if self._params["input_file"]:

            if isGenome(self._params["input_file"]):
                self._queries.append(self._params["input_file"])
            else:
                print("File Error. Input file is an invalid fasta file:\n\tat NeofelisPipline.run()\n\t\tat ",
                    self._params["input_file"], " line 117")
                sys.exit(2)

        elif self._params["input_dir"]:

            self._contents = os.listdir(self._params["input_dir"])

            for self._file in self._contents:
                # mac special case only
                if re.match(r'.DS_Store', self._file, re.IGNORECASE):
                    os.remove(self._params["input_dir"] + "/" + self._file)

                if  isGenome(self._params["input_dir"] + "/" + self._file):
                    self._queries.append(self._params["input_dir"] + "/" + self._file)

            if len(self._queries) == 0:
                print("File Error. Input directory contains no valid fasta files:\n\tat NeofelisPipline.run()\n\t\tat ",
                    self._params["input_file"], " line 128")
                return
        else:

            print("Internal Error. No input provided to Pipeline:\n\tat Pipeline.run():\n\t\tat self._params, line 131")
            return

        try:
            self._event = event.Event()
            self._sentinel = monitor.Monitor(self, self._event, self._queries, self._params)
            self._sentinel.start()
            #self._event.wait()
            #print("joining...")
            if self._sentinel.is_alive():
                try:
                    self._sentinel.join()
                except Exception:
                    pass
        except ThreadError:
            print("Thread Error: Monitor thread failed")
            sys.exit(2)

# __NeofelisPipeline__