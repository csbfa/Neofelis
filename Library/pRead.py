
import subprocess
import select
import fcntl
import os
import errno
from Library import Log, Exceptions


class pRead():

    def __init__(self, name):
        self._log = Log
        self._logger = self._log.new(name)
        self._name = name

    def make_async(self, fd):
        """
        Add the O_NONBLOCK flag to a file descriptor
        """

        fcntl.fcntl(fd, fcntl.F_SETFL, fcntl.fcntl(fd, fcntl.F_GETFL) | os.O_NONBLOCK)

    def read_async(self, fd):
        """
        Read some data from a file descriptor, ignoring EAGAIN errors
        """

        try:
            return fd.read()
        except IOError as e:
            if e.errno != errno.EAGAIN:
                raise e
            else:
                return ''

    def log_fds(self, fds):
        for fd in fds:
            out = self.read_async(fd)
            if out:
                self._logger.info(out)

    def pread(self, command, pipeline):
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
                    raise Exceptions.pReadError("Internal Error occurred in select.select:\n\n" + str(e))

                break

        self._logger.info("Subprocess for %s finished", self._name)
