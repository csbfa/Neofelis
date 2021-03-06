"""
This module use used to extend genes predicted with Genemark and then annotate them using
the function extendGenes.
"""

import os
import re
import functools
from Library import Utils, Exceptions
import com.log.Log as Log


self._logger = Log.new()
self._logger.info("Logging started for Extend")

class Extend():

    def __init__(self, path):
        self._logger.info("Method call: Extend.__init__")
        if not os.path.isdir(path + "/extendedBlasts"):
            os.mkdir(path + "/extendedBlasts")
        self.path = path + "/extendedBlasts"
  
    def getStops(self, genes):
        self._logger.info("Method call: getStops")
        """
        genes:  A list of Iteration objects.

        return: A 2-tuple, first object is a list of where all the forward coding genes stop,
          second is a list of where all the reverse coding genes stop.
        """

        forwardStops = []
        reverseStops = []

        results = map(lambda x: x.location[1], filter(lambda x: x.location[0] < x.location[1], genes))
        for i in results:
            forwardStops.append(i)
        results = map(lambda x: x.location[1], filter(lambda x: x.location[1] < x.location[0], genes))
        for i in results:
            reverseStops.append(i)

        return forwardStops, reverseStops

    def getExtensions(self, genome, genes):
        self._logger.info("Method call: getExtensions")
        """
        genome: The genome as a string.
        genes:  A list of Iteration objects.

        return: A dictionary mapping genes(Iteration objects) to alternative locations where that gene could start.
  
        The alternate starts are calculated by starting at the original start of the gene and iterating backwards.
        When a start codon is found the start of that start codon is added to the list of alternate starts.  If this start
        codon comes before the start of the previous gene then is it still added to the list but the search terminates.
        """

        forwardStops, reverseStops = self.getStops(genes)
        forwardStops.append(1)
        reverseStops.append(len(genome))
        results = {}

        for gene in genes:

            results[gene] = []

            if gene.location[0] < gene.location[1]:

                bound = max(filter((lambda x: x < gene.location[1]), forwardStops))

                for i in range(gene.location[0]-1, 0, -3):
                    if genome[i-3:i] in Utils.startCodons:
                        results[gene].append(i-3)
                        if i <= bound-1:
                            break
                    elif genome[i-3:i] in Utils.stopCodons:
                        break
            else:

                bound = min(filter(lambda x: x > gene.location[1], reverseStops))

                for i in range(gene.location[0], len(genome), 3):

                    if Utils.reverseComplement(genome[i:i+3]) in Utils.startCodons:
                        results[gene].append(i+3)
                        if i >= bound-1:
                            break
                    elif Utils.reverseComplement(genome[i:i+3]) in Utils.stopCodons:
                        break

        return results

    def writeExtensions(self, genome, extensions, name):
        self._logger.info("Method call: writeExtensions")
        """
        genome: The genome as a string.
        extensions: A dictionary mapping genes(Iteration objects) to alternative locations where that gene could start.
  
        This function will write the translation of each possible extension to the file, "extensions.fas".
        """

        try:
            output = open(name + ".extensions.fas", "w")
        except FileNotFoundError as e:
            self._logger.exception("Could not open " + name + ".extensions.fas" + str(e))
            raise Exceptions.ExtendError

        q = 0

        for gene, extensionList in extensions.items():

            for extension in extensionList:

                q += 1

                if gene.location[0] < gene.location[1]:
                    ext = extension+1
                    proteins = Utils.translate(genome[extension:gene.location[1]])
                else:
                    ext = extension
                    proteins = Utils.translate(Utils.reverseComplement(genome[gene.location[1]-1:extension]))

                output.write(">" + gene.query + "~" + str(q) + ":" +  "-".join(map(str, [ext, gene.location[1]])) + "\n")

                for i in range(0, len(proteins), 50):
                    output.write(proteins[i:min(i+50, len(proteins))] + "\n")
      
        output.close()

    def applyExtensions(self, genome, genes, extendedGenes):
        self._logger.info("Method call: applyExtensions")
        """
        genome:        The genome as a string.
        genes:         A dictionary that maps query names to Iteration objects
        extendedGenes: A dictionary that maps query names to Iteration objects, extended versions of genes

        return:        A merging of genes with extendedGenes consisting of the, "better" gene in the event of a conflict

        The merging is done by iterating over the dictionary genes, for each entry in genes extendedGenes
        is iterated over.  If an entry in extendedGenes has a query name that starts with the query name
        of the original gene then that entry is an extension of the original gene.  This extension will replace
        the gene in the new dictionary if it either has an eValue that is lower than the original gene or the extension places
        it within 100 bps of the preceeding gene and is closer to the stop of the preceding gene.
        """

        forwardStops, reverseStops = self.getStops(genes.values())
        forwardStops.append(1)
        reverseStops.append(len(genome))

        def reduceFunction(gene, x, y):
        self._logger.info("Method call: reduceFunction")
            if re.sub(r"(~\d+)~\d+", r"\1", y.query) == gene.query:
                if gene.location[0] < gene.location[1]:
                    stop = max(filter(lambda z: z < gene.location[1], forwardStops))
                    gapSize = y.location[0] - stop
                else:
                    stop = min(filter(lambda z: z > gene.location[1], reverseStops))
                    gapSize = stop - y.location[0]
                if gapSize < 0:
                    return min(x, y, key = lambda z: abs(z.location[0] - stop))
                elif gapSize < 100 or abs(x.eValue - y.eValue) < 10e-5 or Utils.isNaN(x.eValue - y.eValue):
                    return max(x, y, key = lambda z: abs(z.location[1] - z.location[0]))
                else:
                    return min(x, y, key = lambda z: z.eValue)
            else:
                return x

        result = {}
        for gene, geneData in genes.items():
            result[gene] = functools.reduce(functools.partial(reduceFunction, geneData), extendedGenes.values(), geneData)
            if result[gene] != geneData:
                result[gene].color = "0 255 0"
                result[gene].note = "Extended"
        return result

    def extendGenes(self, query, genes, name, blast, database, eValue, result_path, pipeline):
        self._logger.info("Method call: extendGenes")
        """
        query:    File name of the query.
        ganes:    A dictionary that maps query names to Iteration objects
        name:     Name of the genome
        blast:    Location of the installation of blast.
        database: The database to use with blast.
        eValue:   The E Value to use with blast.

        return:   A new dictionary mapping query names to Iteration objects with any better extensions replacing the originals.
  
        This function will search for any possible extensions of the genes in the query.  An extension will replace the original gene in the resulting
        dictionary if it either brings the start of the gene sufficiently close to the end of a previous gene or it has
        a lower eValue.
        """

        if genes is None:
            return None

        genome = Utils.loadGenome(query)

        extensions = self.getExtensions(genome, genes.values())
  
        self.writeExtensions(genome, extensions, name)
        if pipeline.stopped():
            return

        extendedGenes = Utils.cachedBlast(self.path + "/" + name + ".blastp.xml", blast, database, eValue, name + ".extensions.fas", pipeline)
        #os.remove(name + ".extensions.fas")
        return self.applyExtensions(genome, genes, extendedGenes)
