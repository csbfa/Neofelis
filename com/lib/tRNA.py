"""
Function for finding significant RNA sequences.
"""

import os,re,subprocess
from Library import Exceptions
import com.log.Log as Log


self._logger = Log.new()
self._logger.info("Logging started for Terminators")

class tRNA():

    def __init__(self, path):
        self._logger.info("Method call: tRNA.__init__")
        if not os.path.isdir(path + "/tRNAscan-SE"):
            os.mkdir(path + "/tRNAscan-SE")
        self.path = path + "/tRNAscan-SE"

    class TransferRNA():
        """
        Class representing a transfer RNA.
        """

        def __init__(self, start, stop, type, antiCodon, coveScore):
            self._logger.info("Method call: TransferRNA.__init__")
            self.location, self.type, self.antiCodon, self.coveScore = [start, stop], type, antiCodon, coveScore

    def findtRNAs(self, tRNAscanLocation, query, name, pipeline):
        self._logger.info("Method call: findtRNAs")

        """
        tRNAscanLocation: Directory that tRNAscan resides in.
        query:            Name of the fasta file to scan.

        return: List of TransferRNA objects.

        Uses tRNAscan to find transfer RNAs in a fasta file.
        """

        try:
            tRNAscanProcess = subprocess.Popen([tRNAscanLocation + "/tRNAscan-SE", "-B", "-o " + self.path + "/" + name, query], stdout = subprocess.PIPE, stderr = subprocess.PIPE, env = {"PATH" : os.getenv("PATH") + ":" + tRNAscanLocation}, cwd = tRNAscanLocation)
            result = ""
            #tRNAscanProcess.stdout.read()

            if tRNAscanProcess is None:
                print("Error: subprocess pipe could not be opened for tRNAscan-SE")
                raise Exceptions.tRNAError

            err = str(tRNAscanProcess.stderr.read(), 'ascii' )
            if err:
                print("tRNAscan-SE: " + err)
                raise Exceptions.tRNAError

        except Exception:
            self._logger.exception("Exception in tRNAscan-SE subprocess spawning")
            raise Exceptions.tRNAError

        while tRNAscanProcess.poll() is None:
            if pipeline.stopped():
                # try except here for safe kill
                tRNAscanProcess.kill()
                return

            err = str(tRNAscanProcess.stderr.read(), 'ascii')
            if err:
                print("tRNAscan-SE: " + err)
                raise Exceptions.tRNAError

            stuff = str(tRNAscanProcess.stdout.read(), 'ascii')
            result += stuff

        nextRead = str(tRNAscanProcess.stdout.read(), 'ascii')

        while nextRead:
            if pipeline.stopped():
                # try except here for safe kill
                tRNAscanProcess.kill()
                return

            result += nextRead
            nextRead = str(tRNAscanProcess.stdout.read(), 'ascii')
            err = str(tRNAscanProcess.stderr.read(), 'ascii')
            if err:
                print("tRNAscan-SE: " + err)
                raise Exceptions.tRNAError

        if pipeline.stopped():
            return

        transferRNAs = []

        for line in result.split("\n"):
            match = re.match(".+\s+\d+\s+(\d+)\s+(\d+)\s+(\w+)\s+([ACTG?]+)\s+\d+\s+\d+\s+(\d*\.\d*)", line)

            if match:
                transferRNAs.append(self.TransferRNA(int(match.group(1)), int(match.group(2)), match.group(3), match.group(4), float(match.group(5))))

        return transferRNAs
    
