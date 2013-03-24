"""
"""

import os, functools
from Library import Utils
import com.log.Log as Log


self._logger = Log.new()
self._logger.info("Logging started for Intergenic")

class Intergenic():

    def __init__(self, path):
        self._logger.info("Method call: Intergenic.__init__")
        if not os.path.isdir(path + "/intergenicBlasts"):
            os.mkdir(path + "/intergenicBlasts")
        self.path = path + "/intergenicBlasts"

    class Region():
        """
        Class used to store an intergenic region in a genome, stores were the region starts and stops and the
        genes which bracket this region.  Coordinates are those used in blast(starts at one and end index is inclusive).
        """

        def __init__(self, startGene, start, stop, stopGene):
            self._logger.info("Method call: Region.__init__")
            self.startGene = startGene
            self.start = start
            self.stop = stop
            self.stopGene = stopGene

        def __str__(self):
            self._logger.info("Method call: Region.__str__")
            result = ">"
            result += "StartGene = " + str(self.startGene) + ", "
            result += "Start = " + str(self.start) + ", "
            result += "StopGene = " + str(self.stopGene) + ", "
            result += "Stop = " + str(self.stop) + ">"
            return result
  
    def calculateIntergenicRegions(self, genomeLength, genes, minLength = 3):
        self._logger.info("Method call: calculateIntergenicRegions")
        """
        genomeLength: Length of the genome.
        genes:        A list of Iteration objects representing genes.
        minLength:    Minimum length of an intergenic region.

        return:       A 2-tuple, the first element is is a list of the forward strands intergenic regions
                      and the second element is a list of the reverse strands intergenic regions.
  
        Calculates the intergenic regions of a genome.  The intergenic regions are
        calculated iteratively starting with a single intergenic region consisting of the entire genome.  For each gene the regions are
        either splitted or whittled down, then any regions which are smaller than minLength are filtered out, which includes regions of
        negative length which get generated.
        """

        def filterFunction(region):
        self._logger.info("Method call: filterFunction")
            """
            Function for filtering regions which are smaller than minLength, that is, regions which are too small to contain
            an intergenic gene.
            """

            inset = abs(region.stopGene.location[1] - region.stopGene.location[0])/2 if region.stopGene else 0
            if (region.stop + inset - region.start) > float(minLength):
                return region.stop + inset - region.start

        forwardResult, reverseResult = [self.Region(None, 0, genomeLength, None)], [self.Region(None, 0, genomeLength, None)]
        for gene in genes:

            intermediate = []

            if gene.location[0] < gene.location[1]:
                result = forwardResult
                bottom, top = gene.location[0], gene.location[1]
            else:
                result = reverseResult
                bottom, top = genomeLength - gene.location[0] + 1, genomeLength - gene.location[1] + 1

            for region in result:
                if bottom < region.stop <= top:
                    intermediate += [self.Region(region.startGene, region.start, bottom, gene)]
                elif bottom <= region.start < top:
                    intermediate += [self.Region(gene, top, region.stop, region.stopGene)]
                elif region.start < bottom and top < region.stop:
                    intermediate += [self.Region(region.startGene, region.start, bottom, gene), self.Region(gene, top, region.stop, region.stopGene)]
                else:
                    intermediate += [region]

            if gene.location[0] < gene.location[1]:
                forwardResult = filter(filterFunction, intermediate)
            else:
                reverseResult = filter(filterFunction, intermediate)
    
        forwardResult = filter(filterFunction, forwardResult)
        reverseResult = filter(filterFunction, reverseResult)

        return forwardResult, reverseResult

    def findPotentialGenes(self, genome, regions, minLength = 3):
        self._logger.info("Method call: findPotentialGenes")
        """
        genome:    The genome as a string.
        region:    A list of intergenic regions.
        minLength: Minimum length of an intergenic gene.

        return:    A list of 2-tuples, each of which represents the start and stop of an intergenic gene.
  
        Searches for potential genes in regions.  Potential genes are found by starting at the end of the
        region if the end is not bracketed by a gene or the end of the region plus one half the length of
        the end bracketing gene if it is.  This function then steps backwords recording the last stop codon
        encountered.  If a start codon is encountered then the start of the start codon and end of the stop codon
        are saved in a tuple if the start codon comes before the stop of the gene that brackets the end of this region.
        If a start or stop codon is encountered before the start of this region then then the search records the start and stop
        if a start was found and terminates the search for this region.  This process is repeated on each region for each frame.
        The resulting coordinates are string coordinates(first nucleotide is at zero and the ending index is exclusive).
        """

        result = []
        potentials = []
        stop = None

        for region in regions:
            inset = abs(region.stopGene.location[1] - region.stopGene.location[0])/2 if region.stopGene else 0
            for frame in range(3):
                for start in range(int(region.stop+frame+inset), 0, -3):
                    if genome[start-3:start] in Utils.stopCodons:
                        stop = start
                        if start <= region.start:
                            break
                    if genome[start-3:start] in Utils.startCodons and stop and start < region.stop:
                        result.append((start-3, stop))
                        if start <= region.start:
                            break

        for i in filter(lambda x: x[1]-x[0] > int(minLength), result):
            potentials.append(i)

        return potentials
                    
    def writePotentialGenes(self, genome, locations, name):
        self._logger.info("Method call: writePotentialGenes")
        """
        genome:    The genome as a string.
        locations: A list of 2-tuples representing the locations of genes in string coordinates(first nucleotide is at zero and the ending index is exclusive).
  
        Writes all the genes in genome listed locations to "intergenic.fas".  The written
        headers will contain fasta coordinates(first nucleotide is at one and the ending index is inclusive).
        """

        output = open(name + ".intergenics.fas", "w")
        q = 0
        for location in locations:
            q += 1
            if location[0] < location[1]:
                output.write(">intergenic~" + str(q) + ":" + str(location[0]+1) + "-" + str(location[1]) + "\n")
                proteins = Utils.translate(genome[location[0]:location[1]])
            else:
                output.write(">intergenic~" + str(q) + ":" + str(location[0]) + "-" + str(location[1]+1) + "\n")
                proteins = Utils.translate(Utils.reverseComplement(genome[location[1]:location[0]]))
            for i in range(0, len(proteins), 50):
                output.write(proteins[i:min(i+50, len(proteins))] + "\n")

        output.close()

    def removeCommonStops(slef, genes):
        self._logger.info("Method call: removeCommonStops")
        """
        genes: A list of Iteration objects representing genes.
  
        Returns a dictionary just like genes but with any mappings whos value is a gene which shares a stop
        with a more favorable gene in the dictionary removed.  A more favorable gene is any gene which has a higher
        e value or is longer.  First, stopDictionary is made which maps integers to lists of genes which stop
        at that location.  Then the best gene in any set for a given stop is selected to be in the returned dictionary.
        """

        stopDictionary = {}
        for gene in genes.values():
            if gene.location[1] in stopDictionary:
                stopDictionary[gene.location[1]].append(gene)
            else:
                stopDictionary[gene.location[1]] = [gene]

        def reduceFunction(x, y):
            self._logger.info("Method call: reduceFunction")
            """
            Function for determining the more favorable gene.  If both genes have
            infinite e values(no blast hits) then the difference of the e values is NaN
            and the longest gene will be the more favorable one and the one returned.
            Otherwise, the gene with the lower e value will be returned.
            """

            if Utils.isNaN(x.eValue - y.eValue):
                return max(x, y, key = lambda z: abs(z.location[1] - z.location[0]))
            else:
                return min(x, y, key = lambda z: z.eValue)

        result = {}
        for stoppedGenes in stopDictionary.values():
            temp = functools.reduce(reduceFunction, stoppedGenes)
            result[temp.query] = temp

        return result

    def findIntergenics(self, query, genes, name, minLength, blast, database, eValue, result_path, pipeline):
        self._logger.info("Method call: findIntergenics")
        """
        query:     File name of the fasta file.
        genes:     A dictionary that maps query names to Iteration objects
        name:      Name of the genome.
        minLength: Minimum length of any intergenic genes.
        blast:     Location of the installation of blast.
        database:  The database to use with blast.
        eValue:    The e value to use with blast.

        return:    A dictionary that maps query names to Iterations objects, only contains intergenic genes.
  
        Searches for intergenic genes within a genome.  First, all the intergenic regions in the genome are calculated and
        any potential genes in those regions area extracted and written to "intergenics.fas".  This file is then blasted.
        Then the genes in the result of this blast are pruned so that only one intergenic gene may stop at any one
        location.  Finally, the remaining genes are flagged as intergenic and returned.
        """

        if genes is None:
            return None

        results = []

        genome = Utils.loadGenome(query)
        if pipeline.stopped():
            return

        reverseComplementGenome = Utils.reverseComplement(genome)
        if pipeline.stopped():
            return

        openForwardLocations, openReverseLocations = self.calculateIntergenicRegions(len(genome), genes.values(), minLength)
        if pipeline.stopped():
            return
  
        potentialGenes = self.findPotentialGenes(genome, openForwardLocations, minLength)
        if pipeline.stopped():
            return

        reversePotentialGenes = self.findPotentialGenes(reverseComplementGenome, openReverseLocations, minLength)
        if pipeline.stopped():
            return

        results.append(map(lambda x: (len(genome)-x[0], len(genome)-x[1]), reversePotentialGenes))
        if pipeline.stopped():
            return

        for i in results:
            potentialGenes += i
  
        self.writePotentialGenes(genome, potentialGenes, name )
        if pipeline.stopped():
            return
  
        result = Utils.cachedBlast(self.path + "/" + name + ".blastp.xml", blast, database, eValue, name + ".intergenics.fas", pipeline)
        if pipeline.stopped():
            return

        #os.remove(name + ".intergenics.fas")
        result = self.removeCommonStops(result)
        for r in result.values():
            r.intergenic = True
            r.note = "Intergenic"
            r.color = "160 32 240"

        return result
