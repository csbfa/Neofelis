"""
This module contains classes and functions for predicting promoters in a genome.
"""

from Library import Utils
import re
from urllib import request, parse
import functools
import os.path

class Promoters():

    def __init__(self, path):
        if not os.path.isdir(path + "/promoterPredictions"):
            os.mkdir(path + "/promoterPredictions")

    class Promoter():
        """
        Class for storing information about a promoter.
        """

        def __init__(self):
            self.score = 0
            self.position = None
            self.location = None
            self.signal10Location = None
            self.signal35Location = None

        def __str__(self):
            result = "<"
            result += "Score = " + str(self.score) + ", "
            result += "Position = " + str(self.position) + ", "
            result += "Signal10Location = " + str(self.signal10Location) + ", "
            result += "Signal35Location = " + str(self.signal35Location)
            result += ">"
            return result

    def parseBPROM(self, bpromData):
        """
        bpromData: Contents of the body of a BPROM prediction.
  
        return: A list of Promoter objects representing the results of the BPROM prediction
        """

        promoters = re.findall(r"\s+Promoter\s+Pos:\s+(\d+)\s+LDF-\s+(\d+\.?\d*)", bpromData)
        tenBoxes = re.findall(r"\s+-10\s+box\s+at\s+pos.\s+(\d+)\s+([ACGT]+)\s+Score\s+-?\d+", bpromData)
        thirtyFiveBoxes = re.findall(r"\s+-35\s+box\s+at\s+pos.\s+(\d+)\s+([ACGT]+)\s+Score\s+-?\d+", bpromData)

        def parsePromoter(self, promoter, tenBox, thirtyFiveBox):
            result = self.Promoter()
            result.score = float(promoter[1])
            result.position = int(promoter[0])
            result.signal10Location = [int(tenBox[0]), int(tenBox[0])+len(tenBox[1])]
            result.signal35Location = [int(thirtyFiveBox[0]), int(thirtyFiveBox[0])+len(thirtyFiveBox[1])]
            result.location = [min(result.signal10Location + result.signal35Location), max(result.signal10Location + result.signal35Location)]
            return result

        return list(map(parsePromoter, promoters, tenBoxes, thirtyFiveBoxes))

    def cachedBPROM(self, genome, fileName):
        """
        genome: Genome as a string.
        fileName: File to save the BPROM results in.

        return: Results of the BPROM prediction stored in a list of Promoter objects.

        If the file Specified by fileName already exists then this function simply parses the file
        already there.  Also, if a request is made to BPROM and nothing is returned, no file is
        created, the user is warned, and an empty list is returned.
        """

        offset = 25 if ".forward.bprom" in fileName else 50
        direction = "forward" if offset == 50 else "reverse"

        def getPromoters(self):
            input = open(fileName, "r")
            results = self.parseBPROM(input.read())
            input.close()
            return list(results)

        if not os.path.isfile(fileName):

            data = parse.urlencode({"DATA" : genome}).encode('ascii')
            results = request.urlopen("http://linux1.softberry.com/cgi-bin/programs/gfindb/bprom.pl", data)
            resultString = str(results.read())
            results.close()
            prestring_open = resultString.find("<pre>")
            prestring_close = resultString.find("</pre>")
            resultString = resultString[prestring_open:prestring_close]

            resultString = re.sub("<+.+>+", "", resultString).strip()

            if resultString:
                output = open(fileName, "w")
                output.write(resultString)
                output.close()
                return getPromoters(self)
            else:

                print("\nBPROM Error:", "The pipeline will continue to run but BPROM did not process the request for promoters "
                                  "on the " + direction + " strand.  Try again tomorrow")
                return []

        else:
            return getPromoters(self)


    def reverseCoordinates(self, genomeLength, promoter):
        """
        genomeLength: Length of the genome.
        promoter: Promoter object.

        return: Original promoter but with it's coordinates altered so it appears to be on the reverse strand.
        """

        newPromoter = self.Promoter()
        newPromoter.score = promoter.score
        newPromoter.position = genomeLength+1 - promoter.position
        newPromoter.location = map(lambda x: genomeLength+1 - x, promoter.location)
        newPromoter.signal10Location = map(lambda x: genomeLength+1 - x, promoter.signal10Location)
        newPromoter.signal35Location = map(lambda x: genomeLength+1 - x, promoter.signal35Location)

        return newPromoter

    def findPromoters(self, query, name, scoreCutoff, result_path, pipeline):
        """
        query: Name of the query file.
        name: Name of the genome.
        scoreCutoff: Minimum promoter score value for any promoters.

        return: A list of Promoter objects for the forward and reverse strands.
  
        This function uses BPROM to predict promoters and parses the results into the list of Promoter objects
        that are returned. Promoters with a score lower than scoreCutoff are filtered out.
        """

        genome = Utils.loadGenome(query)
        if pipeline.stopped():
            return

        forwardResults = self.cachedBPROM(genome, result_path + "/promoterPredictions/" + name + ".forward.bprom")
        if pipeline.stopped():
            return

        reverseResults = self.cachedBPROM(Utils.reverseComplement(genome), result_path + "/promoterPredictions/" + name + ".reverse.bprom")
        if pipeline.stopped():
            return

        if reverseResults is not None and forwardResults is not None:
            reverseResults = map(functools.partial(self.reverseCoordinates, len(genome)), reverseResults)
            forwardList = []
            reverseList = []

            if pipeline.stopped():
                return

            for item in forwardResults: forwardList.append(item)
            for item in reverseResults: reverseList.append(item)

            return list(filter(lambda x: x.score > scoreCutoff, forwardList + reverseList))
        else:
            return
