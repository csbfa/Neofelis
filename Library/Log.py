import logging, platform, os, sys
from time import gmtime, strftime
from Library import Exceptions


class Log():

    def __init__(self):
        pass

    def start(self, level):

        self._level = level
        logging.captureWarnings(True)

        # Set new log file path. Ensure that the directory exists
        # Ensure that the log directory is not too full. We'll determine this by size and not date archiving
        # This is suboptimal compared native Windows or UNIX size listing, but python does not offer anything faster
        #   without system scripting. However, based on size limit (10MB), this method will not take more than 5ms.
        if platform.system() is "Linux" or platform.system() is "Darwin":

            try:
                if not os.path.isdir("/var/log/Neofelis"):
                    os.mkdir("/var/log/Neofelis")
            except IOError as e:
                raise Exceptions.LoggingError(str(e))

            self._size = 0

            try:
                for (path, dirs, files) in os.walk("/var/log/Neofelis"):
                    for file in files:
                        f = os.path.join(path, file)
                        self._size += os.path.getsize(f)

                if self._size / (1024 * 1024.0) > 10:
                    for (path, dirs, files) in os.walk("/var/log/Neofelis"):
                        for file in files:
                            f = os.path.join(path, file)
                            os.remove(f)
            except IOError as e:
                raise Exceptions.LoggingError(str(e)).with_traceback(sys.exc_info()[2])
            except Exception as e:
                raise Exceptions.LoggingError(str(e)).with_traceback(sys.exc_info()[2])

            fn = "/var/log/Neofelis" + strftime("%Y%m%d%H%M%S", gmtime()) + ".log"

        else:
            raise Exceptions.LoggingError("Error: Incompatible OS detected. Only Linux, Mac, or Windows is "
                                          "supported").with_traceback(sys.exc_info()[2])

        # Verify that the file can be created and does not exist
        try:
            with open(fn) as f: pass
        except IOError as e:
            raise Exceptions.LoggingError("log file\n\n" + fn + "\n\nexists. Uniquely named log file should not exist "
                                          "prior to initialization.\nPlease contact your System Administrator\n\n"
                                          + str(e)).with_traceback(sys.exc_info()[2])

        try:
            logging.basicConfig(filename=fn, level=self._level)
        except FileNotFoundError as e:
            raise Exceptions.LoggingError("log file\n\n" + fn + "\n\nwas not created for logging.\nCheck log directory "
                                                                "permissions or contact your System Administrator\n\n"
                                          + str(e)).with_traceback(sys.exc_info()[2])
        except ValueError as e:
            raise Exceptions.LoggingError("ValueError was encountered while initializing logging:\n\n"
                                          + str(e)).with_traceback(sys.exc_info()[2])
        except Exception as e:
            raise Exceptions.LoggingError("Internal Error: unhandled exception occured:\n\n"
                                          + str(e)).with_traceback(sys.exc_info()[2])

    def new(self, name):
        ll = str("logging." + self._level)
        self._logger = logging.getLogger(name)
        self._logger.setLevel(ll)
        self._ch = logging.StreamHandler()
        self._ch.setLevel(ll)
        self._formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self._ch.setFormatter(self._formatter)
        self._logger.addHandler(self._ch)
        return self._logger

    def get_level(self):
        return self._level


        #elif platform.system() is "Windows":

         #   try:
         #       if not os.path.isdir("%SystemRoot%\System32\Config\Neofelis"):
         #           os.mkdir("%SystemRoot%\System32\Config\Neofelis")
         #   except IOError as e:
         #       raise Exceptions.LoggingError(str(e)).with_traceback(sys.exc_info()[2])

         #   self._size = 0

         #   try:
         #       for (path, dirs, files) in os.walk("%SystemRoot%\System32\Config\Neofelis"):
         #           for file in files:
         #               f = os.path.join(path, file)
         #               self._size += os.path.getsize(f)

         #       if self._size / (1024 * 1024.0) > 10:
         #           for (path, dirs, files) in os.walk("%SystemRoot%\System32\Config\Neofelis"):
         #               for file in files:
         #                   f = os.path.join(path, file)
         #                   os.remove(f)
         #   except IOError as e:
         #       raise Exceptions.LoggingError(str(e)).with_traceback(sys.exc_info()[2])
         #   except Exception as e:
         #       raise Exceptions.LoggingError(str(e)).with_traceback(sys.exc_info()[2])

         #   fn = "%SystemRoot%\System32\Config\Neofelis" + strftime("%Y%m%d%H%M%S", gmtime()) + ".log"

