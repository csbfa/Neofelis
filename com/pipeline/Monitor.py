import multiprocessing, time, sys, math
from threading import RLock, ThreadError
import Library.Processor as processor
from Library.Progress import *
import com.log.Log as Log

self._logger = Log.new()
self._logger.info("Logging started for Monitor")

class Monitor(multiprocessing.Process):
    """

    """

    def __init__(self, manager, event, queries, params):
        self._logger.info("Method call: Monitor.__init__")

        super().__init__()

        self._event = event
        self._hours = 0
        self._minutes = 0
        self._seconds = 0
        self._currtime = 0
        self._manager = manager
        self._params = params
        self._queries = queries
        self._starttime = time.time()
        self._lock = RLock()
        self._totalQueries = len(queries)
        self._event.acquire()

        # naive allocation of maximum threads allowed for pool based on CPU count
        self._size = (multiprocessing.cpu_count() * 2) - 1
        print("Using thread pool size of ", self._size, " for processing")

        try:
            self.progress = ProgressBar(TerminalController(), len(queries))
            self._simple = 0
        except ValueError:
            self._logger.warning("Could not start a Terminal Controller, using simple output")
            self._simple = 1

    def wait(self):
        self._logger.info("Method call: wait")
        """

        """

        if self._params["qsub"]:
            time.sleep(180)
        else:

            self._count = 0

            self._print = ["...", "....", ".....", "......", ".......", "........", ".......", "......", ".....", "...."]

            while self._count <= 180:

                if self._manager.isUpdated():
                    self._manager.reset()
                    return

                for stat in self._print:
                    sys.stdout.write("\r%s" % stat)
                    sys.stdout.flush()
                    self._count+=1
                    time.sleep(1)

            sys.stdout.write("\r")
            sys.stdout.flush()

    def print_simple(self, totalQueries, hours, minutes, seconds):
        self._logger.info("Method call: print_simple")
        """

        """

        if self._params["qsub"]: return

        print("\nNeofelis Pipeline\n\tProcessing ", totalQueries, " queries\n\tElapsed time: ",
            int(math.floor(hours)), " hrs ", int(math.floor(minutes)), " min ",
            int(math.floor(seconds)), " secs\n\tCompleted ", self._manager.getCompleted(), "\n\tFailed ",
            self._manager.getFailed(), end="\n")

    def run(self):
        self._logger.info("Method call: run")
        """

        """

        self._thread = processor.Processor(self._queries.pop(), self._params, self._lock)
        self._thread.subscribe(self._manager)
        self._thread.fire(self._thread)
        self._manager.push(self._thread)

        try:
            self._thread.start()
        except ThreadError:
            self._logger.exception("Thread processing error: Unable to start thread.\n at Pipeline.py")
            return -1

        while self._manager.is_active():

            self._currtime = time.time() - self._starttime
            self._hours = math.floor(self._currtime / 3600)
            self._minutes = math.floor((self._currtime % 3600) / 60)
            self._seconds = (self._currtime % 3600) % 60

            if self._simple:
                if not self._params["qsub"]: self._manager.print_simple(self._totalQueries, self._hours, self._minutes, self._seconds)
            else:
                if not self._params["qsub"]: self.progress.clear()
                if not self._params["qsub"]: self.progress.post( int( math.floor( self._hours )), int( math.floor( self._minutes )), int( math.floor( self._seconds )),
                    self._manager.getCompleted(), self._manager.getFailed())

            while self._manager.size() <= self._size and len( self._queries ) > 0:

                self._thread = processor.Processor(self._queries.pop(), self._params, self._lock)
                self._thread.subscribe(self._manager)
                self._thread.fire(self._thread)
                self._manager.push(self._thread)

                try:
                    self._thread.start()
                except ThreadError:
                    self._logger.exception("Thread processing error: Unable to start thread.\n at Pipeline.py")

            for thread in self._manager.pool():

                if thread.isAlive():
                    if self._simple:
                        if not self._params["qsub"]: print(thread.name, ": ", self._manager.status(thread.name), "%\n")
                    else:
                        if not self._params["qsub"]: self.progress.update(self._manager.status(thread.name), thread.name)

                else:
                    thread.join()
                    self._manager.remove(thread)

            if self._simple:
                self._manager.reset()
                self.wait()
            else:
                self._manager.reset()
                self.wait()
                if not self._params["qsub"]: self.progress.clear()

        if self._simple:
            self.wait()
            if not self._params["qsub"]: self._manager.print_simple(self._totalQueries, self._hours, self._minutes, self._seconds)
        else:
            if not self._params["qsub"]: self.progress.clear()
            if not self._params["qsub"]: self.progress.post( int( math.floor( self._hours )), int( math.floor( self._minutes )), int( math.floor( self._seconds )),
                self._manager.getCompleted(), self._manager.getFailed())

        try:
            self._event.notify()
        except ThreadError:
            self._logger.exception("Thread Error. Unable to join sentinel thread\n\tat NeofelisPipline.finish()\n\t\tat self._sentinel.join()")
            sys.exit(2)

# __Monitor__
