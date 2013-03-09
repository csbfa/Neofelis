"""
"""

import subprocess, re, os
from Library import Exceptions

class Terminators():

    def __init__(self):
        pass

    class Terminator():
        """
        Class used to represent a terminator.
        """

        def __init__(self):
            self.location = None
            self.confidence = None
            self.hpScore = None
            self.tailScore = None

    def writeCoords(self, fileName, name, genes):
        """
        name:  Name of the genome.
        ganes: List of Iteration objects.

        Writes the genes into a .crd file.
        """

        output = open(str(fileName) + ".crd", "w")
        for gene in genes:
            output.write("gene\t%d\t%d\t%s\n" %  (gene.location[0], gene.location[1], name))
        output.close()

    def parseTransterm(self, input):
        """
        input:  Contents of a transterm file.

        return: Contents of the file parsed into a list of Terminator objects.
        """

        matches = re.findall(r"\s+TERM\s+\d+\s+(\d+)\s+-\s+(\d+)\s+[+-]\s+\S+\s+(\d+)\s+(-?\d+.?\d+)\s+(-?\d+.?\d+)", input)

        def buildTerminator(pieces):
            """
            Turns a list of strings into a Terminator object.
            """

            result = self.Terminator()
            result.location = [int(pieces[0]), int(pieces[1])]
            result.confidence = int(pieces[2])
            result.hpScore = float(pieces[3])
            result.tailScore = float(pieces[4])
            return result

        return list(map(buildTerminator, matches))

    def findTerminators(self, query, name, genes, transterm, pipeline):
        """
        query:     File name of the query.
        name:      Name of the genome.
        genes:     List of Iteration objects.
        transterm: Location of the transterm installation.

        return:    A list of Terminator objects.

        This function runs transterm with the query and the genes and parses the results into the return value.
        """

        fileName = os.path.splitext(os.path.split(query)[1])[0]
        self.writeCoords(fileName, name, genes)
        output = ""

        try:
            transtermProcess = subprocess.Popen([transterm + "/transterm", "-p", transterm + "/expterm.dat", query, str(fileName) + ".crd"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if transtermProcess is None:
                print("Error: subprocess pipe could not be opened for Transterm")
                raise Exceptions.TerminatorsError

            err = str(transtermProcess.stderr.read(), 'ascii' )
            if err:
                print("Transterm: " + err)
                raise Exceptions.TerminatorsError

        except Exception:
            print("Exception in Transterm subprocess spawning")
            raise Exceptions.TerminatorsError
  
        while transtermProcess.poll() is None:

            if pipeline.stopped():
                # try except here for safe kill
                transtermProcess.kill()
                return

            output += str(transtermProcess.stdout.read(), 'ascii')
            err = str(transtermProcess.stderr.read(), 'ascii')
            if err:
                print("Terminators: " + err)
                raise Exceptions.TerminatorsError
    
        remaining = str(transtermProcess.stdout.read(), 'ascii')
  
        while remaining:
            if pipeline.stopped():
                # try except here for safe kill
                transtermProcess.kill()
                return

            output += remaining
            remaining = str(transtermProcess.stdout.read(), 'ascii')
            err = str(transtermProcess.stderr.read(), 'ascii')
            if err:
                print("Terminators: " + err)
                raise Exceptions.TerminatorsError

        if pipeline.stopped():
            return

        result = self.parseTransterm(output)
        os.remove(str(fileName) + ".crd")
        return result
