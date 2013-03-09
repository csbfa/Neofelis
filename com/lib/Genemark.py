"""
"""
from Library import Utils, Exceptions
import re, os, subprocess

class Genemark():

    def __init__(self, path):
        if not os.path.isdir(path + "/initialBlasts"):
            os.mkdir(path + "/initialBlasts")
        self.path = path + "/initialBlasts"

    def modifyFastaHeader(self, fileName, name):
        """
        fileName: The name of the file to modify.
        name:     The name of the genome that will be included in the header of each sequence
        """

        try:
            input = open(fileName, "r")
        except FileNotFoundError as e:
            print(e)
            raise Exceptions.GenemarkError

        swap = ""
        for line in input:
            matches = re.search("^>(orf_(\d+)|C2_reset).*$, (\d+ - \d+)", line)
            if matches:
                swap += ">" + name + "~" + ":".join(matches.groups()).replace(" ", "") + "\n"
            else:
                swap += line
        input.close()

        try:
            output = open(fileName, "w")
        except FileNotFoundError as e:
            print(e)
            raise Exceptions.GenemarkError

        output.write(swap)
        output.close()

    def removeInvalidGenes(self, fileName, genomeLength):
        """
        fileName:     Name of the file to modify.
        genomeLength: Length of the genome that the sequences in fileName came from
  
        This function exists because there was a case where genemark predicted a gene that terminated
        2 base pairs after the end of the genome.  This function will remove any genes that
        start or stop outside the genome.
        """

        if not os.path.isfile(fileName):
            try:
                temp = open(fileName, "w+")
                temp.close()
            except FileNotFoundError as e:
                print(e, ": Failed to create file\n")
                raise Exceptions.GenemarkError

        try:
            input = open(fileName, "r")
            swap, reading = "", True
        except FileNotFoundError as e:
            print(e)
            raise Exceptions.GenemarkError

        for line in input:
            location = re.search(r"^>(orf_(\d+)|C2_reset).*$, (\d+) - (\d+)", line)
            if location:
                location = [int(q) for q in location.groups()]
                reading = genomeLength >= location[0] >= 1 and genomeLength >= location[1] >= 1
            if reading:
                swap += line

        input.close()

        output = open(fileName, "w")
        output.write(swap)
        output.close()

    def findGenes(self, query, name, blastLocation, database, eValue, genemark, matrix, result_path, pipeline):
        """
        query:         File name of the query.
        name:          Name of the genome in the query.
        blastLocation: Location of blast installation.
        database:      Name of the database to search.
        eValue:        E value to use when searching.
        genemark:      Location of the genemark installation.
        matrix:        Name of the matrix to use, or None
  
  
        Uses genemark to predict genes in query and then uses blast with the given eValue
        to find annotations for those genes.  If a matrix is not specified the GC program in
        genemark will be used to select a heuristic matrix.
        """

        genome = Utils.loadGenome(query)

        if not matrix:
            gc = int(Utils.getGCContent(genome))
            matrix = genemark + "/" + "heuristic_mat/heu_11_" + str(min(max(30, gc), 70)) + ".mat"

        #try:
        genemarkProcess = subprocess.Popen([genemark + "/gm", "-opq", "-m ", matrix, query], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        #if genemarkProcess is None:
        #    print("Error: subprocess pipe could not be opened for Genemark")
        #    raise Exceptions.GenemarkError

        #err = str(genemarkProcess.stderr.read(), 'ascii' )
        #if err:
        #    print("Genemark: " + err)
        #    raise Exceptions.GenemarkError

        #except Exception:
        #    print("Exception in Genemark subprocess spawning")
         #   raise Exceptions.GenemarkError

        while genemarkProcess.poll() is None:

            if pipeline.stopped():
                # try except here for safe kill
                genemarkProcess.kill()
                return

            #genemarkProcess.stdout.read() # error for this?

            #err = str(genemarkProcess.stderr.read(), 'ascii' )
            #if err:
                #print("Genemark: " + err)
                #raise Exceptions.GenemarkError

        try:

            self.removeInvalidGenes(query + ".orf", len(genome))
            self.modifyFastaHeader(query + ".orf", name)

        except Exceptions.GenemarkError:
            raise Exceptions.GenemarkError

        try:

            result = Utils.cachedBlast(self.path + "/" + name + ".blastp.xml", blastLocation, database, eValue, query + ".orf", pipeline)

            print("Set option to remove of keep files")
            #try:
            #    os.remove(query + ".orf")
            #except FileNotFoundError as e:
            #    print(e, "\ncontinuing processing...")

            #try:
            #    os.remove(query + ".lst")
            #except FileNotFoundError as e:
            #    print(e, "\ncontinuing processing...")

            return result

        except Exceptions.GenemarkError:
            print("cachedBlast failed.")
            raise Exceptions.GenemarkError

