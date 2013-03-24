import subprocess
import select
import fcntl
import os
import errno
from Library import Log, Exceptions
import com.log.Log as Log


self._logger = Log.new()
self._logger.info("Logging started in pRead")

class pRead():

    def __init__(self, name):
        self._logger.info("Method call: __init__")
        self._log = Log
        self._logger = self._log.new(name)
        self._name = name

    def make_async(self, fd):
        self._logger.info("Method call: make_async")
        """
        Add the O_NONBLOCK flag to a file descriptor
        """

        fcntl.fcntl(fd, fcntl.F_SETFL, fcntl.fcntl(fd, fcntl.F_GETFL) | os.O_NONBLOCK)

    def read_async(self, fd):
        self._logger.info("Method call: read_async")
        """
        Read some data from a file descriptor, ignoring EAGAIN errors
        """

        try:
            return fd.read()
        except IOError as e:
            self._logger.exception("Could not read async")
            if e.errno != errno.EAGAIN:
                raise e
            else:
                return ''

    def log_fds(self, fds):
        self._logger.info("Method call: log_fds")
        for fd in fds:
            out = self.read_async(fd)
            if out:
                self._logger.info(out)

    def pread(self, command, pipeline):
        self._logger.info("Method call: pread")
        """
            @params command - formatted command string for subprocess
                    pipeline - instance of thread
        """

        self._logger.info("Subproccess for %s started", self._name)

        self._proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # without `make_async`, `fd.read` in `read_async` blocks.
        self.make_async(self._proc.stdout)
        self.make_async(self._proc.stderr)

        while True:

            if pipeline.stopped():
                self._logger.info("SIGNIT stop broadcasted. Killing subprocess")
                try:
                    self._proc.kill()
                except Exception as e:
                    self._logger.exception("Internal Error: exception when killing subprocess\n\n" + str(e))
                    raise Exceptions.pReadError("Internal Error: exception when killing subprocess:\n\n" + str(e))
                return

            # Wait for data to become available
            # select is UNIX only. TODO compatibility for windows
            try:
                if self._log.get_level() is "CRITICAL":
                    rlist, wlist, xlist = select.select([self._proc.stdout, self._proc.stderr], [], [])
                else:
                    rlist, wlist, xlist = select.select([self._proc.stderr], [], [])
            except Exception as e:
                self._logger.exception("Internal Error occurred in select.select:\n\n" + str(e))
                raise Exceptions.pReadError("Internal Error occurred in select.select:\n\n" + str(e))

            self.log_fds(rlist)
            if self._proc.poll() is not None:

                # Corner case: check if more output was created
                # between the last call to read_async and now

                try:
                    if self._log.get_level() is "CRITICAL":
                        self.log_fds([self._proc.stdout, self._proc.stderr])
                    else:
                        self.log_fds([self._proc.stderr])
                except Exception as e:
                    self._logger.exception("Internal Error occurred in select.select:\n\n" + str(e))
                    raise Exceptions.pReadError("Internal Error occurred in select.select:\n\n" + str(e))

                break

        self._logger.info("Subprocess for %s finished", self._name)
